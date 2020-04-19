from unittest import TestCase
import pandas as pd


class TestPullOptionChain(TestCase):
    def test_pull_option_chain(self):
        from parsers.nseindia import pull_option_chain

        (df,quote,date) = pull_option_chain('KOTAKBANK')
        print(df)
        self.assertIsInstance(df,pd.DataFrame)
        self.assertIsInstance(quote,float)
        self.assertIsInstance(date,str)
