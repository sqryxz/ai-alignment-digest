import unittest
from datetime import datetime, timedelta, UTC
from src.scrapers import AlignmentForumScraper, LessWrongScraper, Post

class TestScrapers(unittest.TestCase):
    def setUp(self):
        self.af_scraper = AlignmentForumScraper()
        self.lw_scraper = LessWrongScraper()

    def test_post_creation(self):
        """Test that Post objects can be created correctly"""
        test_post = Post(
            title="Test Post",
            url="https://example.com/test",
            author="Test Author",
            content="Test content",
            published_date=datetime.now(UTC),
            source="Test Source"
        )
        
        self.assertEqual(test_post.title, "Test Post")
        self.assertEqual(test_post.url, "https://example.com/test")
        self.assertEqual(test_post.author, "Test Author")
        self.assertEqual(test_post.content, "Test content")
        self.assertEqual(test_post.source, "Test Source")

    def test_post_to_dict(self):
        """Test that Post objects can be converted to dictionaries correctly"""
        now = datetime.now(UTC)
        test_post = Post(
            title="Test Post",
            url="https://example.com/test",
            author="Test Author",
            content="Test content",
            published_date=now,
            source="Test Source"
        )
        
        post_dict = test_post.to_dict()
        self.assertEqual(post_dict["title"], "Test Post")
        self.assertEqual(post_dict["url"], "https://example.com/test")
        self.assertEqual(post_dict["author"], "Test Author")
        self.assertEqual(post_dict["content"], "Test content")
        self.assertEqual(post_dict["published_date"], now.isoformat())
        self.assertEqual(post_dict["source"], "Test Source")

    def test_alignment_forum_scraper(self):
        """Test that AlignmentForumScraper can fetch recent posts"""
        posts = self.af_scraper.get_recent_posts(days=1)
        
        # Check that we got some posts
        self.assertIsInstance(posts, list)
        
        # If there are posts, verify their structure
        for post in posts:
            self.assertIsInstance(post, Post)
            self.assertTrue(post.title)
            self.assertTrue(post.url)
            self.assertTrue(post.author)
            self.assertTrue(post.content)
            self.assertIsInstance(post.published_date, datetime)
            self.assertEqual(post.source, "Alignment Forum")
            
            # Check that posts are within the time range
            self.assertGreaterEqual(
                post.published_date,
                datetime.now(UTC) - timedelta(days=1)
            )

    def test_lesswrong_scraper(self):
        """Test that LessWrongScraper can fetch recent posts"""
        posts = self.lw_scraper.get_recent_posts(days=1)
        
        # Check that we got some posts
        self.assertIsInstance(posts, list)
        
        # If there are posts, verify their structure
        for post in posts:
            self.assertIsInstance(post, Post)
            self.assertTrue(post.title)
            self.assertTrue(post.url)
            self.assertTrue(post.author)
            self.assertTrue(post.content)
            self.assertIsInstance(post.published_date, datetime)
            self.assertEqual(post.source, "LessWrong")
            
            # Check that posts are within the time range
            self.assertGreaterEqual(
                post.published_date,
                datetime.now(UTC) - timedelta(days=1)
            )

if __name__ == '__main__':
    unittest.main() 