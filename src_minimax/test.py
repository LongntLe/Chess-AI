import os
import kanban
import unittest
import tempfile

class kanbanTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, kanban.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = kanban.app.test_client()
        #kanban.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(kanban.DATABASE)

    def test_register_status_code(self):
        result = self.app.get('/')

        self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()