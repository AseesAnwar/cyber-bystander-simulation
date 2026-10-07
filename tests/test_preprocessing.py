import tempfile
import unittest
from pathlib import Path

import pandas as pd

from preprocess_cyby23 import clean_dataset, resolve_dataset_path


class PreprocessingTests(unittest.TestCase):
    def test_missing_explicit_dataset_raises_clear_error(self):
        with self.assertRaises(FileNotFoundError):
            resolve_dataset_path("/definitely/not/a/real/cyby23-file.xlsx")

    def test_missing_required_columns_raise_readable_error(self):
        incomplete = pd.DataFrame({"tweet_id": ["1"]})
        with self.assertRaisesRegex(ValueError, "missing required column"):
            clean_dataset(incomplete)

    def test_role_labels_are_normalized(self):
        df = pd.DataFrame(
            {
                "tweet_id": ["1", "2"],
                "reply_id": ["1", "1"],
                "created_at": ["2026-01-01", "2026-01-02"],
                "text": ["source", "reply"],
                "user": ["a", "b"],
                "user_id": ["10", "20"],
                "sentiment": ["negative", "neutral"],
                "Bystander Roles Label": [
                    "",
                    "This person disagree with the main post",
                ],
                "retweet_count": [0, 0],
                "favorite_count": [0, 0],
                "Insult": [0, 0],
                "Threat": [0, 0],
                "Identity_Attack": [0, 0],
                "Profanity": [0, 0],
                "Toxicity": [0.8, 0.2],
                "Severe_Toxicity": [0, 0],
                "polarity": [-0.5, 0.0],
                "subjectivity": [0.5, 0.3],
                "Class label": [1, 0],
            }
        )
        cleaned = clean_dataset(df)
        self.assertEqual(cleaned.loc[1, "normalized_bystander_role"], "defend")
        self.assertTrue(bool(cleaned.loc[1, "is_bystander_reply"]))


if __name__ == "__main__":
    unittest.main()
