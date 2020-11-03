
-----------------------------------find nearby caretaker
SELECT DISTINCT {"this.username"} AS petowner, username AS caretaker
  FROM Users
  WHERE ({"this.postalcode"}/1000) = (postalcode/1000) AND usertype = 'caretaker'
  ;

-----------------------------------calculate salary
CREATE OR REPLACE FUNCTION 
calcMoney(start DATE, endy DATE, price INTEGER) 
RETURNS INTEGER AS $$
    BEGIN RETURN price * (endy - start);
    END; $$
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


CREATE OR REPLACE FUNCTION addSalary()
RETURNS TRIGGER AS $$
BEGIN 
  UPDATE canparttime cp SET salary = salary + 
  (
    SELECT calcMoney(NEW.startday, NEW.endday, 
      (SELECT price FROM dailyprice WHERE
       category = (SELECT category FROM pets P
       WHERE NEW.petname = P.petname AND NEW.pcontact = P.pcontact)
       AND
       rating = (SELECT CEIL(avgrating) FROM canparttime cpt
       WHERE NEW.ccontact = cpt.ccontact)
      )
     )
  )
  WHERE NEW.ccontact = cp.ccontact;
  RETURN NULL;
END;
$$
LANGUAGE PLPGSQL;


DROP TRIGGER IF EXISTS 
newSuccessBidding ON biddings;
CREATE TRIGGER newSuccessBidding
    AFTER UPDATE OF status
    ON biddings
    FOR EACH ROW
    EXECUTE FUNCTION addSalary();

/*
SELECT price INTO dp FROM dailyprice WHERE
category = (SELECT category FROM pets P
            WHERE NEW.petname = P.petname AND NEW.pcontact = P.pcontact)
AND
rating = (SELECT CEIL(avgrating) FROM canparttime cpt
          WHERE NEW.ccontact = cpt.ccontact) 
thisMoney = SELECT calcMoney(NEW.startday, NEW.endday, dp);
UPDATE canparttime cp SET salary = salary + thisMoney
WHERE NEW.ccontact = cp.ccontact
*/


CREATE OR REPLACE FUNCTION log_last_name_changes()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS
$$
BEGIN
  UPDATE canparttime cp SET salary = salary +
  (
    SELECT calcMoney(NEW.startday, NEW.endday, 
      (SELECT price FROM dailyprice WHERE
       category = (SELECT category FROM pets P
       WHERE NEW.petname = P.petname AND NEW.pcontact = P.pcontact)
       AND
       rating = (SELECT CEIL(avgrating) FROM canparttime cpt
       WHERE NEW.ccontact = cpt.ccontact)
      )
    )
  )
  WHERE NEW.ccontact = cp.ccontact;
END;
$$


----- count number of pets alr taken cared by the same caretaker in the selected day
CREATE OR REPLACE FUNCTION findpetnum(ccontact VARCHAR, selectedday DATE)
RETURNS 