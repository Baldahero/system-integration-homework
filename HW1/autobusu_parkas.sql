USE autobusu_parkas;

CREATE TABLE routes (
    mid VARCHAR(10) PRIMARY KEY,
    pavadinimas TEXT,
    trukme INT,
    komentarai TEXT
);

INSERT INTO routes VALUES
('M919', 'Vilnius – Kryžkalnis – Klaipėda', 235, 'Via Elektrėnai');

CREATE TABLE timetables (
    tid INT PRIMARY KEY,
    marsruto_id VARCHAR(10),
    savaites_diena INT,
    isvykimo_laikas TIME,
    galioja_nuo DATE,
    galioja_iki DATE
);

INSERT INTO timetables VALUES
(123654, 'M919', 1, '07:50:00', '2022-01-02', '2026-12-30');

CREATE TABLE stops (
    stid VARCHAR(10) PRIMARY KEY,
    pavadinimas VARCHAR(50),
    longitude DECIMAL(8,6),
    latitude DECIMAL(8,6)
);

INSERT INTO stops VALUES
('STOP001','Vilnius',25.2797,54.6872),
('STOP002','Elektrėnai',24.6630,54.7862),
('STOP003','Kryžkalnis',23.8298,55.4397),
('STOP004','Klaipėda',21.1443,55.7033);

CREATE TABLE stopping_points (
    sid INT PRIMARY KEY,
    tvarkarascio_id INT,
    stoteles_id VARCHAR(10),
    sustojimo_nr INT,
    isvykimo_laikas TIME
);

INSERT INTO stopping_points VALUES
(1,123654,'STOP001',0,'07:50:00'),
(2,123654,'STOP002',1,'08:30:00'),
(3,123654,'STOP003',2,'09:50:00'),
(4,123654,'STOP004',3,'11:45:00');
