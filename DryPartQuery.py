from typing import List
import unittest
import Utility.DBConnector as Connector
from Utility.DBConnector import ResultSet
from psycopg2 import sql


class studentPair:
    def __init__(self, n1=None, n2=None):
        self.n1 = n1
        self.n2 = n2
    
    def __str__(self):
        if self.n1 is None:
            return "empty pair"
        string = "n1 = " + self.n1
        string += ",    "
        string += "n2 = " + self.n2
        return string


def createLearnsTable():
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("CREATE TABLE Learns                                                       \
                     (StudentName   TEXT                                            NOT NULL,   \
                      CourseName    TEXT                                            NOT NULL,   \
                      Grade         INTEGER     CHECK(Grade >= 0 AND Grade <= 100)  NOT NULL,   \
                      Semester      TEXT                                            NOT NULL,   \
                     UNIQUE(StudentName, CourseName))")
        conn.commit()
    except Exception as e:
        print("createLearnsTable exception: " + str(e))
    conn.close()


def dropLearnsTable():
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute("DROP TABLE IF EXISTS Learns")
        conn.commit()
    except Exception as e:
        print("dropLearnsTable exception: " + str(e))
    conn.close()


def addGrade(s_name, c_name, grade, semester):
    conn = None
    try:
        conn = Connector.DBConnector()
        conn.execute(
            sql.SQL(
                "INSERT INTO Learns    \
                 VALUES ({s_name}, {c_name}, {grade}, {semester})"
            ).format(
                s_name = sql.Literal(s_name), 
                c_name = sql.Literal(c_name), 
                grade = sql.Literal(grade), 
                semester = sql.Literal(semester)
            )
        )
        conn.commit()
    except Exception as e:
        print("addGrade exception: " + str(e))
        return -1
    else:
        return 0
    finally:
        conn.close()


def getQueryResult() -> List[studentPair]:
    myQuery2 = "                                                                    \
    SELECT L1.StudentName AS n1, L2.StudentName AS n2                               \
      FROM Learns L1, Learns L2                                                     \
     WHERE L1.CourseName = L2.CourseName                                            \
       AND L1.Semester = L2.Semester                                                \
       AND L1.Grade < L2.Grade                                                      \
     GROUP BY n1, n2                                                                \
    HAVING COUNT(DISTINCT L1.CourseName) =  COUNT(DISTINCT L2.CourseName)           \
       AND COUNT(DISTINCT L1.CourseName) = (SELECT COUNT(*)                         \
                                              FROM Learns                           \
                                             WHERE StudentName = L1.StudentName)    \
       AND COUNT(DISTINCT L2.CourseName) = (SELECT COUNT(*)                         \
                                              FROM Learns                           \
                                             WHERE StudentName = L2.StudentName)"

    conn = None
    _, result = 0, ResultSet()
    ret_val = []
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(myQuery2)
        conn.commit()
    except Exception as e:
        print("getQueryResult exception: " + str(e))
        return ret_val
    finally:
        conn.close()

    for i in range(result.size()):
        ret_val.append(studentPair(result[i]['n1'], result[i]['n2']))
    return ret_val


# myQuery = "                                                                                 \
# SELECT L1.StudentName AS n1,                                                                \
#        L2.StudentName AS n2                                                                 \
#   FROM Learns L1,                                                                           \
#        Learns L2                                                                            \
#  WHERE L1.StudentName NOT IN (SELECT StudentName                                            \
#                                 FROM Learns L3                                              \
#                                WHERE CourseName <> L2.CourseName                            \
#                                   OR Semester NOT IN (SELECT Semester                       \
#                                                         FROM Learns                         \
#                                                        WHERE StudentName = L2.StudentName   \
#                                                          AND CourseName = L3.CourseName)    \
#                                   OR Grade >= (SELECT Grade                                 \
#                                                  FROM Learns                                \
#                                                 WHERE StudentName = L2.StudentName          \
#                                                   AND CourseName = L3.CourseName            \
#                                                   AND Semester = L3.Semester))              \
#    AND L1.StudentName < L2.StudentName"

myQuery = "                                                                                 \
SELECT L1.StudentName AS n1,                                                                \
       L2.StudentName AS n2                                                                 \
  FROM Learns L1,                                                                           \
       Learns L2                                                                            \
 WHERE L1.StudentName NOT IN (SELECT StudentName                                            \
                                FROM Learns L3                                              \
                               WHERE CourseName <> L2.CourseName                            \
)AND L1.StudentName < L2.StudentName"
                                  # OR Semester NOT IN (SELECT Semester                       \
                                  #                       FROM Learns                         \
                                  #                      WHERE StudentName = L2.StudentName   \
                                  #                        AND CourseName = L3.CourseName))   \
                                  # OR Grade >= (SELECT Grade                                 \
                                  #                FROM Learns                                \
                                  #               WHERE StudentName = L2.StudentName          \
                                  #                 AND CourseName = L3.CourseName            \
                                  #                 AND Semester = L3.Semester))              \
   # AND L1.StudentName < L2.StudentName"


class AbstractTest(unittest.TestCase):
    def setUp(self):
        createLearnsTable()

    def tearDown(self):
        dropLearnsTable()

