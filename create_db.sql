PRAGMA foreign_keys = ON;

CREATE TABLE infos(
    centre varchar(20),
    directeur_nom varchar(20),
    nombre_enfants int,
    place varchar(20),
    startdate varchar(10),
    enddate varchar(10)
    );
INSERT INTO infos(
    centre, directeur_nom, nombre_enfants) VALUES (
    NULL, NULL, NULL);

CREATE TABLE fournisseurs(
    id integer PRIMARY KEY,
    NOM varchar(20)
    );

CREATE TABLE codecompta(
    CODE int PRIMARY KEY,
    NOM varchar(20),
    code_analytique_id int,
    FOREIGN KEY (code_analytique_id) REFERENCES code_analytique(code) ON DELETE NO ACTION
    );

CREATE TABLE type_payement (
    id integer PRIMARY KEY,
    NOM varchar(20)
    );

INSERT INTO type_payement (NOM) VALUES ('Chèque');
INSERT INTO type_payement (NOM) VALUES ('Espèces');
INSERT INTO type_payement (NOM) VALUES ('Carte Bancaire');
INSERT INTO type_payement (NOM) VALUES ('Autre');

CREATE TABLE code_analytique (
    code INTEGER PRIMARY KEY,
    nom VARCHAR(20)
    );

CREATE TABLE pieces_comptables(
    id integer PRIMARY KEY,
    Fournisseur_id integer NOT NULL,
    Date varchar(10),
    total real,
    TypePayement_id int NOT NULL,
    cheque_number int,
    FOREIGN KEY (Fournisseur_id) REFERENCES fournisseurs(id) ON DELETE NO ACTION,
    FOREIGN KEY (TypePayement_id) REFERENCES type_payement(id) ON DELETE NO ACTION
    );
    
CREATE TABLE subdivisions(
    id INTEGER PRIMARY KEY,
    designation,
    piece_comptable_id INTEGER,
    code_compta_id INTEGER NOT NULL,
    code_analytique_id INTEGER,
    prix REAL,
    FOREIGN KEY (piece_comptable_id) REFERENCES pieces_comptables(id)
    ON DELETE CASCADE,
    FOREIGN KEY (code_compta_id) REFERENCES codecompta(code) ON DELETE NO ACTION,
    FOREIGN KEY (code_analytique_id) REFERENCES code_analytique(code) ON DELETE NO ACTION
    );

CREATE UNIQUE INDEX idx_CODE ON codecompta (CODE);
CREATE UNIQUE INDEX idx_NOM_FO ON fournisseurs (NOM);
CREATE UNIQUE INDEX idx_CODE_AN ON code_analytique (CODE);

CREATE TABLE inputs(
    id INTEGER PRIMARY KEY,
    date varchar(10),
    montant real,
    comment varchar(30) 
    );
    
CREATE TABLE retraits_liquide(
    id INTEGER PRIMARY KEY,
    date VARCHAR(10),
    montant real
    );
