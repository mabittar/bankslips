CREATE TABLE IF NOT EXISTS bankslips (
    debt_id VARCHAR NOT NULL PRIMARY KEY UNIQUE,  
    name VARCHAR NOT NULL,                        
    government_id VARCHAR NOT NULL,               
    email VARCHAR NOT NULL,                       
    debt_amount FLOAT NOT NULL,                   
    debt_due_date TIMESTAMP NOT NULL,             
    bankslip_file VARCHAR NULL,                   
    propagated BOOLEAN NOT NULL DEFAULT FALSE,    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);