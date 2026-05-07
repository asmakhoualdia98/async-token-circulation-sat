import os
import math
from pysat.formula import CNF
from pysat.card import CardEnc, EncType

class GraphModel:
    def __init__(self, graph_type, num_nodes, modulus, mode, model_option, daemon):
    
        self.graph_type = graph_type
        self.num_nodes = num_nodes
        self.modulus = modulus
        
        # Execution mode (CONV, DIV)
        self.mode = mode.upper()
        
        # Model option (INI, OE)
        self.model_option = model_option.upper()
        
        # Daemon
        self.daemon = daemon.upper()
        
        # Number of allowed configurations
        self.max_steps = 3 * self.num_nodes * (self.num_nodes - 1) // 2


    # --------------------------------------------------
    # Variables
    # --------------------------------------------------

    def st(self, i, t, v):
        return i * self.max_steps * self.modulus + t * self.modulus + v + 1

    def enb(self, i, t, v):
        base = self.st(self.num_nodes - 1,
                        self.max_steps - 1,
                        self.modulus - 1)
        return base + i * self.max_steps * self.modulus + t * self.modulus + v + 1

    def tok(self, i, t):
        base = self.enb(self.num_nodes - 1,
                        self.max_steps - 1,
                        self.modulus - 1)
        return base + i * self.max_steps + t + 1

    def twoact(self, i, j):
        base = self.tok(self.num_nodes - 1, self.max_steps - 1)
        return base + i * self.num_nodes + j + 1
        
    def inact(self, i):
        base = self.twoact(self.num_nodes - 1,self.num_nodes - 1)
        return base + i + 1
        
    def act(self, i, t):
        base = self.inact(self.num_nodes - 1)
        return base + i * self.max_steps + t + 1 
        
    def cyc(self, t):
        return self.act(self.num_nodes - 1, self.max_steps - 1) + t + 1

    def sim(self, i, t, value):
        return self.cyc(self.max_steps - 1) + i * self.max_steps * self.modulus + t * self.modulus + value + 1

    # --------------------------------------------------
    # Clock uniqueness
    # --------------------------------------------------

    def add_uniqueness_clauses(self, cnf):
        top_id = self.sim(self.num_nodes - 1, self.max_steps - 1, self.modulus - 1)
        for t in range(self.max_steps):
            for i in range(self.num_nodes):
                variables = [self.st(i, t, v) for v in range(self.modulus)]
                card = CardEnc.equals(
                    lits=variables,
                    bound=1,
                    encoding=EncType.cardnetwrk,
                    top_id=top_id
                )
                top_id = card.nv
                cnf.extend(card.clauses)

    # --------------------------------------------------
    # Activation constraints
    # --------------------------------------------------

    def add_act_clauses(self, cnf):
        n = self.num_nodes
        m = self.modulus
        t_max = self.max_steps

        for t in range(t_max - 1):
            cnf.append([self.act(p,t) for p in range(n)])
            for p in range(n):
                cnf.append(
                    [-self.act(p, t)] +
                    [self.tok(p, t)]
                )
 
    # --------------------------------------------------
    # Update rules
    # --------------------------------------------------
   
    def add_update_clauses(self, cnf):
        n = self.num_nodes
        m = self.modulus
        t_max = self.max_steps
    
        for t in range(t_max - 1):
    
            # -------------------------
            # p ≠ 0
            # -------------------------
            for p in range(1, n):
                pred = (p - 1) % n
    
                for v in range(m):
                    
                    # Enabled AND activated → takes the value of the predecessor
                    cnf.append([
                        self.enb(p, t, v),
                        -self.st(pred, t, v),
                        -self.act(p, t),
                        self.st(p, t + 1, v)
                    ])

                    # Enabled BUT not enabled → persistence
                    cnf.append([
                        -self.st(p, t, v),
                        self.act(p, t),
                        self.st(p, t + 1, v)
                    ])
    
                    # Not activatable → persistence (equality with the predecessor)
                    cnf.append([
                        -self.enb(p, t, v),
                        self.st(p, t + 1, v)
                    ])
    
            # -------------------------
            # p = 0 
            # -------------------------
            for v in range(m):
    
                # Enabled AND enabled → increment modulo m
                cnf.append([
                    -self.enb(0, t, v),
                    -self.act(0, t),
                    self.st(0, t + 1, (v + 1) % m)
                ])
    
                # Enabled BUT not enabled → persistence
                cnf.append([
                    -self.st(0, t, v),
                    self.act(0, t),
                    self.st(0, t + 1, v)
                ])
    
                # Not activatable → persistence
                cnf.append([
                    self.enb(0, t, v),
                    -self.st(0, t, v),
                    self.st(0, t + 1, v)
                ])


    # --------------------------------------------------
    # Authorization constraints (checked at tf-1)
    # --------------------------------------------------

    def add_enb_clauses(self, cnf):
        n = self.num_nodes
        
        for t in range(self.max_steps):
            for p in range(n):
                pred_p = (p - 1) % n
                for v in range(self.modulus):
                    cnf.append([-self.enb(p, t, v), self.st(p, t, v)])
                    cnf.append([-self.enb(p, t, v), self.st(pred_p, t, v)])
                    cnf.append([
                        self.enb(p, t, v),
                        -self.st(p, t, v),
                        -self.st(pred_p, t, v)
                    ])

    # --------------------------------------------------
    # Token constraints
    # --------------------------------------------------

    def add_token_clauses_direct(self, cnf):
        n = self.num_nodes
        m = self.modulus
        t_m = self.max_steps
        
        for t in range(t_m):

            cnf.append(
                [-self.tok(0, t)] +
                [self.enb(0, t, v) for v in range(m)]
            )
            
            for p in range(1, n):
                for v in range(m):
                    cnf.append([-self.tok(p, t), -self.enb(p, t, v)])
                    
    def add_token_clauses_indirect(self, cnf):
        n = self.num_nodes
        m = self.modulus
        t_m = self.max_steps
        
        for t in range(t_m):
            for p in range(1, n):
                for v in range(m):
                    cnf.append([-self.tok(p, t), -self.enb(p, t, v)])
                    
                cnf.append(
                    [self.tok(p, t)] +
                    [self.enb(p, t, v) for v in range(m)]
                )
        
    # --------------------------------------------------
    # Convergence constraint
    # --------------------------------------------------
    
    def add_non_convergence(self, cnf):
        n = self.num_nodes
        t_max = self.max_steps
        variables = [self.tok(i, t_max - 1) for i in range(n)]
        top_id = cnf.nv
        card = CardEnc.atleast(
            lits=variables,
            bound=2,
            encoding=EncType.cardnetwrk,
            top_id=top_id
        )
        cnf.extend(card.clauses)
        
    # --------------------------------------------------
    # Divergence constraint
    # --------------------------------------------------
    
    def add_divergence(self, cnf):
        
        # Formule 1
        
        clause = [self.cyc(t) for t in range(1, self.max_steps)]
        cnf.append(clause)
            
        # Formule 2 :
        
        for t in range(1, self.max_steps):
            for i in range(self.num_nodes):
                clause = [self.sim(i, t, v) for v in range(self.modulus)] + [-self.cyc(t)]
                cnf.append(clause)
     
        
        # Formule 3 :
        for t in range(1, self.max_steps):
            for i in range(self.num_nodes):
                for v in range(self.modulus):
                
                    clause1 = [
                        self.st(i, 0, v), 
                        -self.sim(i,t, v)
                    ]
                    
                    cnf.append(clause1)
                    
                    clause2 = [
                        self.st(i, t, v), 
                        -self.sim(i,t, v)
                    ]
                    
                    cnf.append(clause2)
                    
        
    
    def add_div_tok(self, cnf):
        n = self.num_nodes
        
        variables = [self.tok(i, 0) for i in range(n)]
        top_id = cnf.nv
        card = CardEnc.atleast(
            lits=variables,
            bound=2,
            encoding=EncType.cardnetwrk,
            top_id=top_id
        )
        cnf.extend(card.clauses)
        
    # --------------------------------------------------
    # Non sequential daemon constraint
    # --------------------------------------------------
      
    def add_non_seq_clauses(self, cnf):
        n = self.num_nodes
        m = self.modulus

        cnf.append([self.twoact(p, q)
            for q in range(n)
            for p in range(q)
            ])
        
        for q in range(n):
            for p in range(q):
                clause1 = [
                    -self.twoact(p, q), 
                    self.act(p,0)
                ]
                cnf.append(clause1)
                
                clause2 = [
                    -self.twoact(p, q), 
                    self.act(q,0)
                ]
                cnf.append(clause2)
                
    # --------------------------------------------------
    # Non synchronous daemon constraint
    # --------------------------------------------------
      
    def add_non_synch_clauses(self, cnf):
        n = self.num_nodes
        m = self.modulus
        t_max = self.max_steps

        cnf.append([self.inact(p) for p in range(n)])
        for p in range(n):
            clause1 = [
                self.tok(p,0), 
                -self.inact(p)
            ]
            cnf.append(clause1)
            
            clause2 = [
                -self.act(p,0), 
                -self.inact(p)
            ]
            cnf.append(clause2)
            
    # --------------------------------------------------
    # Synchronous daemon constraint
    # --------------------------------------------------
      
    def add_synch_clauses(self, cnf):
        n = self.num_nodes
        m = self.modulus
        t_max = self.max_steps

        for t in range(t_max - 1):
            for p in range(n):
                
                clause1 = [
                    -self.tok(p,t), 
                    self.act(p,t)
                ]
                
                cnf.append(clause1)
            
            
    # --------------------------------------------------
    # Shift constraint
    # --------------------------------------------------
      
    def add_shifted_conf(self, cnf):
        cnf.append([self.st(0,0,0)])

    # --------------------------------------------------
    # Generation
    # --------------------------------------------------

    def generate_cnf(self, output_path):
        cnf = CNF()
        self.add_uniqueness_clauses(cnf)
        self.add_act_clauses(cnf)
        self.add_update_clauses(cnf)
        self.add_enb_clauses(cnf)
        self.add_token_clauses_direct(cnf)
        
        
        if self.mode == "CONV":
            self.add_non_convergence(cnf)

        elif self.mode == "DIV":
            self.add_divergence(cnf)
            self.add_div_tok(cnf)

        if self.model_option == "OE":
            self.add_shifted_conf(cnf)
            
        if self.model_option == "INI":
            pass
            
        # --- DAEMONS ASSUPTIONS---
        
        if self.daemon == "NON-SEQ":
            self.add_token_clauses_indirect(cnf)
            self.add_non_seq_clauses(cnf)
        
        elif self.daemon == "NON-SYNC":
            self.add_token_clauses_indirect(cnf)
            self.add_non_synch_clauses(cnf)
        
        elif self.daemon == "SYNC":
            self.add_token_clauses_indirect(cnf)
            self.add_synch_clauses(cnf)
        
        elif self.daemon == "DIS-UNFAIR":
            pass
                

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cnf.to_file(output_path)
        print(f"✅ CNF file generated: {output_path}")
