from typing import List
from typing import Tuple
import unittest
import Utility.DBConnector as Connector
from Utility.DBConnector import ResultSet
from psycopg2 import sql

my_query = "                                                                        \
    SELECT L1.StudentName AS n1, L2.StudentName AS n2                               \
      FROM Learns L1, Learns L2                                                     \
     WHERE L1.CourseName = L2.CourseName                                            \
       AND L1.Semester = L2.Semester                                                \
       AND L1.Grade < L2.Grade                                                      \
     GROUP BY n1, n2                                                                \
    HAVING COUNT(DISTINCT L1.CourseName) = COUNT(DISTINCT L2.CourseName)            \
       AND COUNT(DISTINCT L1.CourseName) = (SELECT COUNT(*)                         \
                                              FROM Learns                           \
                                             WHERE StudentName = L1.StudentName)    \
       AND COUNT(DISTINCT L2.CourseName) = (SELECT COUNT(*)                         \
                                              FROM Learns                           \
                                             WHERE StudentName = L2.StudentName)"


# ChatGPT_query = "SELECT l1.StudentName AS n1, l2.StudentName AS n2   \
#             FROM Learns l1, Learns l2       \
#             WHERE l1.StudentName < l2.StudentName   \
#                 AND l1.CourseName = l2.CourseName   \
#                 AND l1.Semester = l2.Semester   \
#             GROUP BY l1.StudentName, l2.StudentName \
#             HAVING COUNT(DISTINCT l1.CourseName) = COUNT(Distinct l2.CourseName)    \
#                 AND MIN(l1.Grade)< MIN(l2.Grade)"


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
        return False
    else:
        return True
    finally:
        conn.close()


def getQueryResult() -> List[Tuple]:
    conn = None
    _, result = 0, ResultSet()
    ret_val = []
    try:
        conn = Connector.DBConnector()
        _, result = conn.execute(my_query)
        conn.commit()
    except Exception as e:
        print("getQueryResult exception: " + str(e))
        return ret_val
    finally:
        conn.close()

    for i in range(result.size()):
        pair = (result[i]['n1'], result[i]['n2'])
        ret_val.append(pair)
    return ret_val



class AbstractTest(unittest.TestCase):
    def setUp(self):
        createLearnsTable()

    def tearDown(self):
        dropLearnsTable()

