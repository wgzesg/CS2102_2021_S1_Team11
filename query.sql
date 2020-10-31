
-----------------------------------find nearby caretaker
SELECT DISTINCT {"this.username"} AS petowner, username AS caretaker
  FROM Users
  WHERE ({"this.postalcode"}/1000) = (postalcode/1000) AND usertype = 'caretaker'
  ;

-----------------------------------calculate salary
CREATE OR REPLACE FUNCTION 
calculate_salary(start DATE, end DATE, price INTEGER) 
RETURN INT AS
    'BEGIN RETURN price * (end - start)) + 3000;
    END;'
LANGUAGE plpgsql;

CREAET VIEW salarylist (ccontact, salary) AS
    WITH tb1 AS (
        SELECT r.ccontact AS tbcontact, r.rating AS tbrating, r.startday AS tbstart, r.enddat AS tbend, p.category AS tbcategory
        FROM reviews r INNERJOIN pets p ON (r.petname = p.petname AND r.pcontact = p.pcontact) 
    )
    SELECT t.tbcontact AS ccontact, calculate_salary(t.tbstart, t.tbend, d.price) AS salary
    FROM tb1 t INNERJOIN dailyprice d ON (t.tbcategory = d.category)
    WHERE EOMONTH(endday) = {"end of this month"}
 ;

SELECT ccontact, SUM(salary)
FROM salarylist 
GROUP BY ccontact
;

-----------------------------------calculate working days

