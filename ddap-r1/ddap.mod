# sets and parameters
param moduleCapacity, >= 0;

param maxNode, >= 0, integer;
set Nodes= 1..maxNode;                                   # just for checking parameter validity

set Links;
param link_nodeA{ Links}, in Nodes;
param link_nodeZ{ Links}, in Nodes;
param link_moduleCost{ Links}, >= 0;


set Demands;
param demand_volume{ Demands}, >= 0, default 0;          # h_d

param demand_maxPath{ Demands}, >= 0, default 0;         # P_d
set Demand_pathLinks{ d in Demands, dp in 1..demand_maxPath[ d]} within Links;  # paths as sets of links


# decision variables
var demandPath_flow{ d in Demands, 1..demand_maxPath[ d]}, >= 0, integer;    # x_dp
var link_moduleCount{ Links}, >= 0, integer;                                 # number of modules
var link_load{ Links}, >= 0;
var link_capacity{ Links}, >= 0;

# constraints
subject to cns_demand_satisfaction{ d in Demands}:
    sum{ dp in 1..demand_maxPath[ d]} demandPath_flow[ d, dp]= demand_volume[ d];

subject to cns_link_load{ e in Links}:
    link_load[ e]= sum{ d in Demands} sum{ p in 1..demand_maxPath[ d]: e in Demand_pathLinks[ d, p]} demandPath_flow[ d, p]; 

subject to cns_link_capacity{ e in Links}:
    link_capacity[ e]== moduleCapacity* link_moduleCount[ e];

subject to cns_link_nonOverloading{ e in Links}:
    link_load[ e]<= link_capacity[ e];


# objectives
minimize capacityCost: sum{ e in Links} link_moduleCount[ e]* link_moduleCost[ e];


