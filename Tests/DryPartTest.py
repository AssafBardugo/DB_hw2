import unittest
import DryPartQuery
from DryPartQuery import AbstractTest

class DryPartTest(AbstractTest):
    def test_Base(self):
        self.assertEqual(0, DryPartQuery.addGrade('Assaf', 'DB', 100, 'Spring'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Assaf', 'OS', 100, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Avi', 'OS', 90, 'Spring'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Avi', 'DS', 85, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Avi', 'DB', 67, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Dana', 'DB', 86, 'Spring'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Dana', 'OS', 85, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Miki', 'OS', 90, 'Spring'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Miki', 'DS', 85, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Noa', 'DS', 90, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Noa', 'OS', 91, 'Spring'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Rotem', 'DB', 100, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Rotem', 'DS', 97, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Yossi', 'DB', 77, 'Spring'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Yossi', 'OS', 84, 'Winter'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Yuval', 'DB', 100, 'Spring'), "Should work")
        self.assertEqual(0, DryPartQuery.addGrade('Yuval', 'OS', 91, 'Winter'), "Should work")

        pairs = DryPartQuery.getQueryResult()
        if not pairs:
            print("No pairs exist")
        else:
            for pair in pairs:
                print(pair)


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)

