"""Unit tests for reviewboard.reviews.views.DownloadRawDiffView."""

from __future__ import unicode_literals

from reviewboard.diffviewer.parser import DiffParser
from reviewboard.testing import TestCase


class DownloadRawDiffViewTests(TestCase):
    """Unit tests for reviewboard.reviews.views.DownloadRawDiffView."""

    fixtures = ['test_users', 'test_scmtools']

    # Bug #3384
    def test_sends_correct_content_disposition(self):
        """Testing DownloadRawDiffView sends correct Content-Disposition"""
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)

        self.create_diffset(review_request=review_request)

        response = self.client.get('/r/%d/diff/raw/' % review_request.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename=diffset')

    # Bug #3704
    def test_normalize_commas_in_filename(self):
        """Testing DownloadRawDiffView removes commas in filename"""
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)

        # Create a diffset with a comma in its name.
        self.create_diffset(review_request=review_request, name='test, comma')

        response = self.client.get('/r/%d/diff/raw/' % review_request.pk)
        content_disposition = response['Content-Disposition']
        filename = content_disposition[len('attachment; filename='):]
        self.assertFalse(',' in filename)

    def test_crlf(self):
        """ """
        diff = (
            b'--- README\trevision 123\r\n'
            b'+++ README\trevision 123\r\n'
            b'@@ -1 +1 @@\r\n'
            b'-Hello, world!\r\n'
            b'+Hello, everybody!\r\n'
        )
        self._test_line_endings(diff)

    def test_lf(self):
        """ """
        diff = (
            b'--- README\trevision 123\n'
            b'+++ README\trevision 123\n'
            b'@@ -1 +1 @@\n'
            b'-Hello, world!\n'
            b'+Hello, everybody!\n'
        )
        self._test_line_endings(diff)

    def _test_line_endings(self, in_diff):
        """ """
        parser = DiffParser(in_diff)
        files = parser.parse()

        repository = self.create_repository(tool_name="Subversion")

        review_request = self.create_review_request(create_repository=False,
                                                    repository=repository,
                                                    publish=True)
        diffset = self.create_diffset(review_request=review_request)

        self.create_filediff(diffset, diff=files[0].data, crlf=parser.crlf)

        response = self.client.get('/r/%d/diff/raw/' % review_request.pk)

        out_diff = response.content

        self.assertEqual(in_diff, out_diff)
