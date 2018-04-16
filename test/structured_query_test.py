import unittest

from GenomeSearchUtil.GenomeSearchUtilIndexer import _eval_structured_query


class StructuredQueryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sline1 = 'b0001_CDS_1	CDS	NC_000913.3	190	+	66	b0001,ECK0001; JW4367,thrL,NP_414542.1	leader,Amino acid biosynthesis: Threonine,product:thr operon leader peptide	GO:0009088,threonine biosynthetic process'.split('\t')
        cls.sline2 = 'b0002	gene	NC_000913.3	337	+	2463	1.1.1.3,thrA,ECK0002; Hs; JW0001; thrA1; thrA2; thrD,2.7.2.4,b0002,NP_414543.1	enzyme,Amino acid biosynthesis: Threonine,product:Bifunctional aspartokinase/homoserine dehydrogenase 1	GO:0005737,cytoplasm,GO:0009086,methionine biosynthetic process,GO:0009088,threonine biosynthetic process,GO:0009090,homoserine biosynthetic process'.split('\t')
        cls.props_map = {
            "feature_id": {"col": 2, "type": ""},
            "feature_type": {"col": 3, "type": ""},
            "contig_id": {"col": 4, "type": ""},
            "start": {"col": 5, "type": "n"},
            "strand": {"col": 6, "type": ""},
            "length": {"col": 7, "type": "n"},
            "function": {"col": 9, "type": ""}
        }

    def test_invalid_input(self):
        with self.assertRaisesRegexp(ValueError, "Unrecognised field"):
            _eval_structured_query(self.sline1, {"foo": "bar"}, self.props_map)

        with self.assertRaisesRegexp(ValueError, "should be a dictionary"):
            _eval_structured_query(self.sline1, "meh", self.props_map)

        with self.assertRaisesRegexp(ValueError, "should be a list"):
            _eval_structured_query(self.sline1, {'$and': "meh"}, self.props_map)

        with self.assertRaisesRegexp(ValueError, "should be a list"):
            _eval_structured_query(self.sline1, {'$or': "meh"}, self.props_map)

    def test_field_query(self):
        self.assertTrue(_eval_structured_query(self.sline1, {"feature_id": "b0001_CDS_1"},
                                               self.props_map))
        self.assertTrue(_eval_structured_query(self.sline1, {"feature_id": "b0001_CDS_1",
                                                             "feature_type": "CDS"},
                                               self.props_map))
        self.assertFalse(_eval_structured_query(self.sline1, {"feature_id": "b0001_CDS_1",
                                                              "feature_type": "gene"},
                                                self.props_map))
        self.assertFalse(_eval_structured_query(self.sline1, {"feature_id": "b0001"},
                                                self.props_map))

    def test_not_query(self):
        self.assertFalse(_eval_structured_query(self.sline1, {"$not": {"feature_id": "b0001_CDS_1"}},
                                                self.props_map))
        self.assertTrue(_eval_structured_query(self.sline1, {"$not": {"feature_id": "b0001"}},
                                               self.props_map))
        self.assertTrue(_eval_structured_query(self.sline1, {"$not": {"feature_id": "b0001",
                                                                      "feature_type": "gene"}},
                                               self.props_map))

    def test_or_query(self):
        self.assertTrue(_eval_structured_query(self.sline1, {"$or": [{"feature_id": "b0001_CDS_1"},
                                                                     {"feature_type": "CDS"}]},
                                               self.props_map))
        self.assertTrue(_eval_structured_query(self.sline1, {"$or": [{"feature_id": "b0001_CDS_1"},
                                                                     {"feature_type": "gene"}]},
                                               self.props_map))
        self.assertTrue(_eval_structured_query(self.sline2, {"$or": [{"feature_id": "b0001_CDS_1"},
                                                                     {"feature_type": "gene"}]},
                                               self.props_map))
        self.assertFalse(_eval_structured_query(self.sline1, {"$or": [{"feature_id": "meh"},
                                                                      {"feature_type": "gene"}]},
                                                self.props_map))
        self.assertTrue(_eval_structured_query(self.sline1, {"feature_id": ["b0001_CDS_1", "b0001"]},
                                               self.props_map))

    def test_and_query(self):
        self.assertTrue(_eval_structured_query(self.sline1, {"$and": [{"feature_type": "CDS"},
                                                                      {"feature_type": "CDS"}]},
                                               self.props_map))
        self.assertFalse(_eval_structured_query(self.sline1, {"$and": [{"feature_type": "CDS"},
                                                                       {"feature_type": "gene"}]},
                                                self.props_map))

    def test_combo_queries(self):
        self.assertTrue(_eval_structured_query(self.sline1,
                                               {"$not": {"$or": [{"feature_id": "meh"},
                                                                 {"feature_type": "gene"}]}},
                                               self.props_map))
        self.assertTrue(_eval_structured_query(self.sline1,
                                               {"$or": [{"$not": {"feature_id": "meh"}},
                                                        {"feature_type": "gene"}]},
                                               self.props_map))
        self.assertFalse(_eval_structured_query(self.sline1,
                                                {"$or": [{"$not": {"feature_id": "b0001_CDS_1"}},
                                                         {"feature_type": "gene"}]},
                                                self.props_map))
        self.assertTrue(_eval_structured_query(self.sline1,
                                               {"$and": [{"$not": {"feature_id": "meh"}},
                                                         {"feature_type": "CDS"}]},
                                               self.props_map))
