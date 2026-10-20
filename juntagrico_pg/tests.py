from unittest import skipUnless

from django.contrib.auth.models import Permission
from django.db import connection
from django.test import override_settings
from django.urls import reverse

from juntagrico.tests import JuntagricoTestCase

requires_postgres = skipUnless(connection.vendor == 'postgresql', 'requires postgresql')


class PGTests(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.load_members()
        cls.default_member = cls.member
        cls.member.user.user_permissions.add(Permission.objects.get(codename='can_sql'))
        cls.member.user.save()

    def sql(self, sql):
        return self.assertPost(reverse('jpg:sql'), {'sql': sql}).content.decode()

    def test_view_protection(self):
        self.assertGet(reverse('jpg:home'), 302, self.member2)
        self.assertGet(reverse('jpg:sql'), 302, self.member2)

    def test_home(self):
        self.assertGet(reverse('jpg:home'))

    def test_sql_get(self):
        self.assertGet(reverse('jpg:sql'), 405)

    def test_sql_post(self):
        response = self.assertPost(reverse('jpg:sql'), {'sql': 'SELECT 1 AS one'})
        # rowcount differs between database backends
        self.assertTrue(response.content.startswith(b'+-----+\n| one |\n+=====+\n| 1   |\n+-----+\nROWS: '))

    def test_sql_response_is_plain_text(self):
        response = self.assertPost(reverse('jpg:sql'), {'sql': "SELECT '<script>alert(1)</script>'"})
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_sql_is_logged(self):
        with self.assertLogs('juntagrico_pg', 'INFO') as logs:
            self.sql('SELECT 1')
        self.assertIn(f'(id {self.member.user.pk}): SELECT 1', logs.output[0])

    def test_sql_error_is_logged(self):
        with self.assertLogs('juntagrico_pg', 'WARNING') as logs:
            output = self.sql('SELECT * FROM nonexistent_table')
        self.assertIn('nonexistent_table', output)
        self.assertIn('failed', logs.output[0])

    @override_settings(JPG_MAX_ROWS=2)
    def test_sql_max_rows(self):
        output = self.sql("SELECT 'a' AS x UNION ALL SELECT 'b' UNION ALL SELECT 'c'")
        self.assertIn('| a |', output)
        self.assertIn('| b |', output)
        self.assertNotIn('| c |', output)
        self.assertIn('Only the first 2 rows are shown.', output)

    def test_sql_special_command(self):
        output = self.sql('\\h')
        self.assertIn('SELECT', output)
        output = self.sql('\\h select')
        self.assertIn('Syntax:', output)

    def test_sql_special_command_not_allowed(self):
        output = self.sql("\\copy juntagrico_member TO '/tmp/members.csv'")
        self.assertIn('Command \\copy is not supported', output)

    def test_sql_error(self):
        self.assertPost(reverse('jpg:sql'))

    @requires_postgres
    def test_sql_special_command_postgres(self):
        self.assertIn('juntagrico_member', self.sql('\\dt'))
        self.assertIn('juntagrico_member', self.sql('\\dt juntagrico_mem*'))
        self.assertNotIn('juntagrico_depot ', self.sql('\\dt juntagrico_mem*'))
        output = self.sql('\\d juntagrico_member')
        self.assertIn('first_name', output)

    @requires_postgres
    @override_settings(JPG_STATEMENT_TIMEOUT=100)
    def test_sql_statement_timeout(self):
        self.assertIn('statement timeout', self.sql('SELECT pg_sleep(2)'))

    @requires_postgres
    @override_settings(JPG_STATEMENT_TIMEOUT=100)
    def test_sql_statement_timeout_is_reset(self):
        self.sql('SELECT 1')
        # timeout must not stick to the connection
        with connection.cursor() as cur:
            cur.execute('SHOW statement_timeout')
            self.assertEqual(cur.fetchone()[0], '0')
