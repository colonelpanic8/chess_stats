import os
import tempfile

import testify as T
from flask import Flask

from chess_stats import models


class ChessStatsSandboxedTestCase(T.TestCase):

    @T.setup_teardown
    def setup_db(self):
        self.db_fd, file_path = tempfile.mkstemp()
        self.app = Flask(__name__)
        models.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{0}".format(
            file_path
        )
        self.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{0}".format(
            file_path
        )
        models.db.init_app(self.app)
        with self.app.app_context():
            models.db.create_all()
            self.models = models
            yield
        os.close(self.db_fd)