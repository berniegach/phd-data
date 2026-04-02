CREATE TABLE Employee(
  employee_nr TEXT PRIMARY KEY,
  name TEXT,
  job_description TEXT,
  manager_nr TEXT REFERENCES Employee(employee_nr) ON DELETE NO ACTION
);
CREATE TABLE Dummy(dummy_int INT);

INSERT INTO Employee VALUES('U000001', 'Han van Krieken', 'rector magnificus', NULL);
INSERT INTO Employee VALUES('U000012', 'Sijbrand de Jong', 'dean', 'U000001');
INSERT INTO Employee VALUES('U000013', 'Noëlle Aarts', 'director ISIS', 'U000012');
INSERT INTO Employee VALUES('U000014', 'Britta Redlich', 'director FELIX', 'U000012');
INSERT INTO Employee VALUES('U000015', 'Arjen de Vries', 'director ICIS' ,'U000012');
INSERT INTO Employee VALUES('U000016', 'Tom Heskes', 'head DaS', 'U000015');
INSERT INTO Employee VALUES('U000017', 'Djoerd Hiemstra', 'prof. databases' ,'U000016');
INSERT INTO Employee VALUES('U000018', 'Negin Ghasemi', 'phd student', 'U000017');
INSERT INTO Employee VALUES('U000010', 'Ms. X', 'independent consultant', NULL);
INSERT InTO Employee VALUES('U000011', 'Ms. Y', 'secretary', 'U000010');
