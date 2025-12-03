'''CityWithoutWalls.py

Full simulation (Option C) — 12 operators per role (60 total).
Each operator is grounded in sources from the user's "Homelessness Stuff.docx".
Each transition's banner includes an APA-like citation line plus the filecite token
so the provenance is explicit to the system.

Single global turn-taking variable: TURN_START (only one global).
State authoritative turn: self.turn (and numeric view properties).
'''

# METADATA
SOLUZION_VERSION = "5.0"
PROBLEM_NAME = "CityWithoutWalls"
PROBLEM_VERSION = "3.0"
PROBLEM_AUTHORS = ['Shreyas, Lauren (adapted by ChatGPT)']
PROBLEM_CREATION_DATE = "02-December-2025"
PROBLEM_DESC = "Complex hybrid simulation of policies to reduce homelessness; 5 active stakeholder roles + observers."

# ROLES
NEIGHBORHOODS = 0
BUSINESS = 1
MEDICAL = 2
SHELTERS = 3
UNIVERSITY = 4
OBSERVER = 5

ROLE_NAMES = ["Neighborhoods", "Business", "Medical", "SheltersServices", "University", "Observer"]

# Single global turn seed (only one turn variable globally)
TURN_START = NEIGHBORHOODS

DEBUG = False

# Imports
from soluzion5 import Basic_State, Basic_Operator as Operator, ROLES_List, add_to_next_transition
import Select_Roles as sr
import math, random

# File-citations used from the uploaded spec (these tokens point to the uploaded doc)
# Note: these tokens are the file_search citations referencing your Homelessness Stuff.docx
# We'll include these tokens inside each operator transition so the transition banner
# includes the provenance marker the system can trace back.
FC = {
    'neigh': ":contentReference[oaicite:1]{index=1}",   # general neighborhoods & role resources
    'spec':  ":contentReference[oaicite:2]{index=2}",   # spec & evidence links
    'medical':":contentReference[oaicite:3]{index=3}",
    'shelters':":contentReference[oaicite:4]{index=4}",
    'university':":contentReference[oaicite:5]{index=5}",
    'business':":contentReference[oaicite:6]{index=6}",
    'evidence':":contentReference[oaicite:7]{index=7}",
    'overview':":contentReference[oaicite:8]{index=8}"
}

def int_to_name(i):
    try:
        return ROLE_NAMES[i]
    except:
        return f"Role_{i}"

# ---------------- State ----------------
class State(Basic_State):
    def __init__(self, old=None):
        if old is None:
            # turn (authoritative)
            self.turn = TURN_START

            # Demographic subpopulations (initial values from your spec doc)
            self.pop_families = 2800
            self.pop_youth = 1800
            self.pop_chronic = 3600
            self.pop_veterans = 1500
            self.homeless_population = (self.pop_families + self.pop_youth +
                                        self.pop_chronic + self.pop_veterans)

            # Housing tiers (units)
            self.shelter_capacity = 1400
            self.transitional_units = 600
            self.permanent_units = 2200

            # Service resources
            self.social_workers = 120
            self.outreach_teams = 8
            self.medical_vans = 3

            # Budgets (thousands)
            self.shelter_budget = 800.0
            self.neighborhood_budget = 900.0
            self.business_budget = 750.0
            self.medical_budget = 900.0
            self.university_budget = 450.0

            # Political / economic / legal metrics (0-100 or k$)
            self.public_support = 52.0
            self.economy_index = 100.0
            self.legal_pressure = 10.0
            self.policy_momentum = 0.0
            self.debt = 0.0

            self.last_action = ""
            self.round = 0
            self.trend_history = [int(self.homeless_population)] * 10

        else:
            # copy constructor
            self.turn = old.turn
            self.pop_families = old.pop_families
            self.pop_youth = old.pop_youth
            self.pop_chronic = old.pop_chronic
            self.pop_veterans = old.pop_veterans
            self.homeless_population = old.homeless_population
            self.shelter_capacity = old.shelter_capacity
            self.transitional_units = old.transitional_units
            self.permanent_units = old.permanent_units
            self.social_workers = old.social_workers
            self.outreach_teams = old.outreach_teams
            self.medical_vans = old.medical_vans
            self.shelter_budget = old.shelter_budget
            self.neighborhood_budget = old.neighborhood_budget
            self.business_budget = old.business_budget
            self.medical_budget = old.medical_budget
            self.university_budget = old.university_budget
            self.public_support = old.public_support
            self.economy_index = old.economy_index
            self.legal_pressure = old.legal_pressure
            self.policy_momentum = old.policy_momentum
            self.debt = old.debt
            self.last_action = old.last_action
            self.round = old.round
            self.trend_history = list(old.trend_history)

    # Compatibility for Select_Roles/Web_SZ5_01: numeric properties required
    @property
    def current_role_num(self):
        return self.turn

    @property
    def current_role(self):
        return self.turn

    @property
    def whose_turn(self):
        return self.turn

    def recalc_population(self):
        self.homeless_population = (self.pop_families + self.pop_youth +
                                    self.pop_chronic + self.pop_veterans)

    def record_trend(self):
        self.trend_history.append(int(self.homeless_population))
        if len(self.trend_history) > 10:
            self.trend_history.pop(0)

    def __str__(self):
        return (f"Round {self.round} - Turn: {int_to_name(self.turn)}\n"
                f"Total Homeless: {self.homeless_population} (f:{self.pop_families}, y:{self.pop_youth}, c:{self.pop_chronic}, v:{self.pop_veterans})\n"
                f"Capacity: shelter {self.shelter_capacity}, trans {self.transitional_units}, perm {self.permanent_units}\n"
                f"Budgets (k$): S={self.shelter_budget:.0f}, N={self.neighborhood_budget:.0f}, B={self.business_budget:.0f}, M={self.medical_budget:.0f}, U={self.university_budget:.0f}\n"
                f"Public support: {self.public_support:.1f}%, Economy: {self.economy_index:.1f}, Legal pressure: {self.legal_pressure:.1f}\n"
                f"Debt: ${self.debt:.0f}k, Momentum: {self.policy_momentum:.1f}\n"
                f"Last action: {self.last_action}\n")

    def is_goal(self):
        # goal: 20% reduction overall AND public_support >=45 AND legal pressure <25
        return (self.homeless_population <= int(0.8 * 10700) and
                self.public_support >= 45.0 and
                self.legal_pressure < 25.0)

    def goal_message(self):
        if self.is_goal():
            return f"Goal: homeless {self.homeless_population}, support {self.public_support:.1f}%, legal {self.legal_pressure:.1f}"
        return ""

SESSION = None

PLAYABLE_ROLES = [NEIGHBORHOODS, BUSINESS, MEDICAL, SHELTERS, UNIVERSITY]
NUM_PLAYERS = len(PLAYABLE_ROLES)

def next_player_index(current_role_index):
    idx = PLAYABLE_ROLES.index(current_role_index)
    return PLAYABLE_ROLES[(idx + 1) % NUM_PLAYERS]

def update_turn(state):
    state.turn = next_player_index(state.turn)
    if state.turn == PLAYABLE_ROLES[0]:
        state.round += 1

def can_act_as(role, s):
    return s.turn == role

# ---------- small helper functions ----------
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def percent_of(n, pct):
    return max(0, int(round(n * (pct/100.0))))

def add_transition_with_sources(s_new, title, effects_text, apa_text, fc_token):
    # Create a transition banner combining APA-like text and the filecite token
    banner = f"--- Transition: {title}\nSource: {apa_text}\n{fc_token}\nEffects:\n{effects_text}"
    add_to_next_transition(banner, s_new)

# ---------- Operator generator (to keep code compact) ----------
def make_op(name, role, cost_k, deltas, apa_source, fc_token):
    """
    - name: display name
    - role: role index that can act
    - cost_k: dict mapping budget names to amount deducted (k$)
    - deltas: dict mapping state attributes to additive changes or functions
    - apa_source: human-readable APA-style source string
    - fc_token: filecite token
    """
    def op_fn(s, name=name, cost_k=cost_k, deltas=deltas, apa_source=apa_source, fc_token=fc_token):
        news = State(s)
        add_to_next_transition(f"{int_to_name(role)} -> {name}", news)
        # apply costs
        for bk, amt in cost_k.items():
            if getattr(news, bk) < amt:
                # insufficient budget -> partial or fail depending on operator
                news.last_action = f"{int_to_name(role)} attempted '{name}' but lacked budget (${amt}k needed)."
                # add transition with source and a note that it failed
                add_transition_with_sources(news, f"{int_to_name(role)} → {name}", "Action failed: insufficient budget.", apa_source, fc_token)
                update_turn(news)
                news.record_trend()
                return news
            setattr(news, bk, getattr(news, bk) - amt)
        # apply deltas; deltas values can be numeric or callables (news -> mutate)
        effects = []
        for k, v in deltas.items():
            if callable(v):
                # function receives news and returns a textual description
                desc = v(news)
                if desc:
                    effects.append(desc)
            else:
                # numeric additive
                if hasattr(news, k):
                    before = getattr(news, k)
                    after = before + v
                    setattr(news, k, after)
                    effects.append(f"{k}: {before} -> {after}")
        # recalc derived
        news.recalc_population()
        news.record_trend()
        # compose effects text
        eff_text = "\n".join(effects) if effects else "(no direct numeric effect recorded)"
        add_transition_with_sources(news, f"{int_to_name(role)} → {name}", eff_text, apa_source, fc_token)
        news.last_action = f"{int_to_name(role)} performed '{name}'."
        update_turn(news)
        return news
    return Operator(name, lambda s, role=role: can_act_as(role, s), op_fn)

# ---------------- Operators (12 per role) ----------------
# For readability: each operator includes an APA-like source string that
# refers to the relevant documents from your uploaded spec (filecite tokens included below).

# ---- SHELTERS (12 operators) ----
shelters_ops = []

# 1 Emergency Expansion (big effect on capacity, families/vets)
shelters_ops.append(make_op(
    "Emergency Expansion (beds +300)",
    SHELTERS,
    {'shelter_budget': 300.0},
    {
        'shelter_capacity': 300,
        'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families, 10))) or f"families reduced by {percent_of(ns.pop_families,10)}"),
        'pop_veterans': lambda ns: (setattr(ns, 'pop_veterans', max(0, ns.pop_veterans - percent_of(ns.pop_veterans, 12))) or f"veterans reduced by {percent_of(ns.pop_veterans,12)}")
    },
    "Life After Transition and HUD reports (evidence for capacity effects).",
    FC['shelters']
))

# 2 Community Faith Partnerships (volunteers + caseworkers)
shelters_ops.append(make_op(
    "Community Partnership (vols & caseworkers)",
    SHELTERS,
    {'shelter_budget': 80.0},
    {
        'social_workers': 6,
        'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic, 1.5))) or f"chronic -{percent_of(ns.pop_chronic,1.5)}"),
        'policy_momentum': 0.6
    },
    "Shelter-community partnerships reduce chronic homelessness and build momentum (HUD, HSRI evaluations).",
    FC['shelters']
))

# 3 Housing First Pilot (permanent placements)
shelters_ops.append(make_op(
    "Housing First Pilot (perm +150)",
    SHELTERS,
    {'shelter_budget': 420.0},
    {
        'permanent_units': 150,
        'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic, 8))) or f"chronic -{percent_of(ns.pop_chronic,8)}"),
        'public_support': 2.5,
        'economy_index': -1.5
    },
    "Housing First & PSH evaluations indicate strong reductions in chronic homelessness (Hilton Foundation eval.).",
    FC['shelters']
))

# 4 Volunteer Training (social worker upskilling)
shelters_ops.append(make_op(
    "Volunteer Training (social workers +3)",
    SHELTERS,
    {'shelter_budget': 40.0},
    {'social_workers': 3, 'public_support': 1.0},
    "Volunteer & caseworker training improves placement rates (HSRI / HUD cleaning & program reports).",
    FC['shelters']
))

# 5 Rent Assistance Fund (prevents inflow)
shelters_ops.append(make_op(
    "Rent Assistance Fund (prevention)",
    SHELTERS,
    {'shelter_budget': 220.0},
    {
        'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families, 6))) or f"families -{percent_of(ns.pop_families,6)}"),
        'pop_youth': lambda ns: (setattr(ns, 'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth, 4))) or f"youth -{percent_of(ns.pop_youth,4)}"),
        'policy_momentum': 1.0,
        'public_support': 1.8
    },
    "Rent assistance/rapid rehousing prevents inflow (HUD/HSRI evidence).",
    FC['shelters']
))

# 6 Maintenance Deferral (cost-cutting, side-effects)
shelters_ops.append(make_op(
    "Defer Maintenance (gain budget, lose beds)",
    SHELTERS,
    {},  # no budget required; this adds budget
    {
        'shelter_budget': 60.0,
        'shelter_capacity': -40,
        'public_support': -2.5,
        'legal_pressure': 2.0
    },
    "Cutting maintenance boosts short-term funds but reduces safe capacity (HUD & shelter ops reports).",
    FC['shelters']
))

# 7 Rapid Rehousing Expansion
shelters_ops.append(make_op(
    "Rapid Rehousing Boost",
    SHELTERS,
    {'shelter_budget': 200.0},
    {
        'transitional_units': 60,
        'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families, 9))) or f"families -{percent_of(ns.pop_families,9)}"),
        'policy_momentum': 1.2
    },
    "Rapid rehousing reduces family homelessness and is cost-effective (NLIHC/HUD briefs).",
    FC['shelters']
))

# 8 Outreach van increase
shelters_ops.append(make_op(
    "Add Outreach Vans",
    SHELTERS,
    {'shelter_budget': 90.0},
    {'outreach_teams': 2, 'pop_youth': lambda ns: (setattr(ns, 'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth,6))) or f"youth -{percent_of(ns.pop_youth,6)}")},
    "Mobile outreach & triage reduces youth unsheltered counts (Commonwealth Fund & PMC articles).",
    FC['shelters']
))

# 9 Case Management Intensification
shelters_ops.append(make_op(
    "Intensify Case Management",
    SHELTERS,
    {'shelter_budget': 120.0},
    {'social_workers': 5, 'policy_momentum': 0.9, 'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,5))) or f"chronic -{percent_of(ns.pop_chronic,5)}")},
    "Case management is linked to higher housing retention (HSRI evaluations).",
    FC['shelters']
))

# 10 Temporary Encampment Support (sanctioned encampment)
shelters_ops.append(make_op(
    "Sanction Encampment (sanctioned services)",
    SHELTERS,
    {'shelter_budget': 150.0},
    {'shelter_capacity': 80, 'public_support': -1.0, 'legal_pressure': -2.5},
    "Sanctioned encampments can reduce acute harms but elicit neighborhood concerns (PMC studies).",
    FC['shelters']
))

# 11 Partner with Medical Quarter
shelters_ops.append(make_op(
    "Partner: Medical Support (onsite clinics)",
    SHELTERS,
    {'shelter_budget': 160.0, 'medical_budget': 60.0},
    {'medical_vans': 1, 'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,7))) or f"chronic -{percent_of(ns.pop_chronic,7)}")},
    "Shelter-medical partnerships improve outcomes and reduce ER use (Commonwealth Fund; HSRI).",
    FC['shelters']
))

# 12 Data & Evaluation (partner with Univ)
shelters_ops.append(make_op(
    "Evaluation & Data Sharing (with Univ)",
    SHELTERS,
    {'shelter_budget': 60.0, 'university_budget': 70.0},
    {'policy_momentum': 1.6, 'public_support': 0.8},
    "Rigorous evaluation multiplies program effectiveness by informing policy (USICH, university studies).",
    FC['shelters']
))

# ---- NEIGHBORHOODS (12 operators) ----
neighbor_ops = []

neighbor_ops.append(make_op(
    "Media Campaign (reframe homelessness)",
    NEIGHBORHOODS,
    {'neighborhood_budget': 120.0},
    {'public_support': 6.0, 'legal_pressure': -3.0},
    "Media & grassroots campaigns can shift public perception (SAGE journal references in spec).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Block New Low-Income Development (NIMBY action)",
    NEIGHBORHOODS,
    {'neighborhood_budget': 40.0},
    {'permanent_units': -50, 'public_support': 2.0, 'legal_pressure': 4.0},
    "NIMBY blocking reduces new units and increases legal conflict (spec: Berkeley Law Clinic & literature).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Local Voucher Matching Fund",
    NEIGHBORHOODS,
    {'neighborhood_budget': 180.0},
    {'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families,7))) or f"families -{percent_of(ns.pop_families,7)}"), 'permanent_units': 20, 'policy_momentum': 0.8, 'public_support': 3.0},
    "Local vouchers leverage private funds to increase permanence (HUD & local program evidence).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Civic Forum (reduce tensions)",
    NEIGHBORHOODS,
    {'neighborhood_budget': 30.0},
    {'legal_pressure': -2.0, 'public_support': 1.0},
    "Civic engagement reduces complaint rates & legal conflicts (community practice literature).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Fund Private Security (pushout)",
    NEIGHBORHOODS,
    {'neighborhood_budget': 90.0},
    {'public_support': 3.0, 'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', ns.pop_chronic + int(percent_of(ns.homeless_population,0.6))) or f"chronic +{int(percent_of(ns.homeless_population,0.6))}"), 'legal_pressure': 2.0},
    "Private security/sweeps reduce local visibility but displace people (Berkeley Law Clinic, PMC8427990).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Infrastructure Grants (convert trans->perm)",
    NEIGHBORHOODS,
    {'neighborhood_budget': 240.0},
    {'transitional_units': -80, 'permanent_units': 72, 'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families,1))) or f"families -{percent_of(ns.pop_families,1)}"), 'policy_momentum': 1.5},
    "Local capital grants can convert stock and increase permanent supply (urban studies evidence).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Community Food & Outreach Sponsorship",
    NEIGHBORHOODS,
    {'neighborhood_budget': 60.0},
    {'outreach_teams': 1, 'public_support': 1.2, 'pop_youth': lambda ns: (setattr(ns, 'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth,3))) or f"youth -{percent_of(ns.pop_youth,3)}")},
    "Community outreach reduces short-term unsheltered counts and improves support (spec links).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Neighborhood Rapid Response to Eviction Spikes",
    NEIGHBORHOODS,
    {'neighborhood_budget': 200.0},
    {'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families,10))) or f"families -{percent_of(ns.pop_families,10)}"), 'policy_momentum': 1.0},
    "Eviction prevention programs reduce inflow (NLIHC/HUD reports).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Public Space Design (reduce congregation)",
    NEIGHBORHOODS,
    {'neighborhood_budget': 140.0},
    {'public_support': 1.6, 'legal_pressure': -1.2},
    "Designing public spaces can reduce conflict and complaints (urban planning literature).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Property Value Assistance (tax incentive to support programs)",
    NEIGHBORHOODS,
    {'neighborhood_budget': 200.0},
    {'permanent_units': 30, 'public_support': 0.9},
    "Neighborhood incentives can unlock private conversions (spec evidence).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Neighborhood-led Transitional Housing Project",
    NEIGHBORHOODS,
    {'neighborhood_budget': 260.0},
    {'transitional_units': 90, 'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families,6))) or f"families -{percent_of(ns.pop_families,6)}"), 'policy_momentum': 1.2},
    "Locally-managed transitional projects show good placement outcomes (HUD/HSRI).",
    FC['neigh']
))

neighbor_ops.append(make_op(
    "Neighborhood Monitoring & Data (complaint tracking)",
    NEIGHBORHOODS,
    {'neighborhood_budget': 40.0},
    {'legal_pressure': -0.8, 'public_support': 0.4},
    "Data & transparent monitoring reduces friction and builds trust (community practice).",
    FC['neigh']
))

# ---- BUSINESS (12 operators) ----
business_ops = []

business_ops.append(make_op(
    "Tax Incentives for Affordable Housing",
    BUSINESS,
    {'business_budget': 200.0},
    {'permanent_units': 120, 'economy_index': 1.8, 'public_support': 1.2},
    "Developer incentives increase supply and create short-term jobs (evidence in spec).",
    FC['business']
))

business_ops.append(make_op(
    "Fund Job Readiness Programs",
    BUSINESS,
    {'business_budget': 150.0},
    {'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families,5))) or f"families -{percent_of(ns.pop_families,5)}"),
     'pop_youth': lambda ns: (setattr(ns, 'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth,12))) or f"youth -{percent_of(ns.pop_youth,12)}"),
     'public_support': 2.2},
    "Job programs reduce unemployment-driven homelessness (evidence: HSRI / NAEH).",
    FC['business']
))

business_ops.append(make_op(
    "Clean & Sweep (sanitation)",
    BUSINESS,
    {'business_budget': 70.0},
    {'public_support': 2.5, 'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', ns.pop_chronic + int(percent_of(ns.homeless_population,0.4))) or f"displaced +{int(percent_of(ns.homeless_population,0.4))}"), 'legal_pressure': 1.5},
    "Sweeps improve perceptions but often displace people and increase harms (NAEH, Berkeley Law Clinic).",
    FC['business']
))

business_ops.append(make_op(
    "Public-Private Transitional Housing",
    BUSINESS,
    {'business_budget': 320.0},
    {'transitional_units': 90, 'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families,4))) or f"families -{percent_of(ns.pop_families,4)}"), 'public_support': 1.8},
    "Public-private partnerships can create transitional capacity (case studies).",
    FC['business']
))

business_ops.append(make_op(
    "Lobby for Restrictive Ordinances",
    BUSINESS,
    {'business_budget': 100.0},
    {'legal_pressure': 5.0, 'economy_index': 0.8, 'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', ns.pop_chronic + int(percent_of(ns.homeless_population,0.7))) or f"displaced +{int(percent_of(ns.homeless_population,0.7))}")},
    "Business-driven ordinances often increase legal pressure and displacement (Berkeley Law Clinic).",
    FC['business']
))

business_ops.append(make_op(
    "Volunteer Street Ambassadors",
    BUSINESS,
    {'business_budget': 80.0},
    {'outreach_teams': 2, 'public_support': 1.5, 'pop_youth': lambda ns: (setattr(ns, 'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth,5))) or f"youth -{percent_of(ns.pop_youth,5)}")},
    "Ambassador programs link unsheltered to services and reduce visible homelessness (spec links).",
    FC['business']
))

business_ops.append(make_op(
    "Clean Streets + Social Service Coupling",
    BUSINESS,
    {'business_budget': 180.0},
    {'public_support': 2.8, 'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,2))) or f"chronic -{percent_of(ns.pop_chronic,2)}")},
    "Coupling sanitation with services reduces displacement harms (studies in spec).",
    FC['business']
))

business_ops.append(make_op(
    "Small Business Microgrants to Hire",
    BUSINESS,
    {'business_budget': 120.0},
    {'economy_index': 1.2, 'public_support': 1.0},
    "Hiring incentives support employment routes out of homelessness (economic program evidence).",
    FC['business']
))

business_ops.append(make_op(
    "Sponsor Transitional Unit Conversions",
    BUSINESS,
    {'business_budget': 240.0},
    {'transitional_units': 70, 'policy_momentum': 0.9},
    "Business sponsorships can add transitional slots (case studies).",
    FC['business']
))

business_ops.append(make_op(
    "Support Low-Barrier Shelters",
    BUSINESS,
    {'business_budget': 160.0},
    {'shelter_capacity': 120, 'pop_chronic': lambda ns: (setattr(ns, 'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,3))) or f"chronic -{percent_of(ns.pop_chronic,3)}"), 'public_support': 0.6},
    "Private funding for low-barrier shelters reduces acute homelessness and hospital burden (PMC references).",
    FC['business']
))

business_ops.append(make_op(
    "Coalition with Shelters for Employer Placement",
    BUSINESS,
    {'business_budget': 140.0},
    {'pop_families': lambda ns: (setattr(ns, 'pop_families', max(0, ns.pop_families - percent_of(ns.pop_families,3))) or f"families -{percent_of(ns.pop_families,3)}"), 'policy_momentum': 0.5},
    "Employer partnerships can speed housing exits via employment (HSRI evidence).",
    FC['business']
))

business_ops.append(make_op(
    "Sponsor University Pilot (housing innovation)",
    BUSINESS,
    {'business_budget': 200.0, 'university_budget': 50.0},
    {'transitional_units': 40, 'policy_momentum': 1.0},
    "Business funding for university pilots can create scalable prototypes (spec references).",
    FC['business']
))

# ---- MEDICAL (12 operators) ----
medical_ops = []

medical_ops.append(make_op(
    "Deploy Mobile Clinics",
    MEDICAL,
    {'medical_budget':160.0},
    {'medical_vans':2, 'pop_chronic': lambda ns: (setattr(ns,'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,6))) or f"chronic -{percent_of(ns.pop_chronic,6)}"), 'public_support':2.8},
    "Mobile clinics and triage reduce chronic unsheltered morbidity and link to housing (Commonwealth Fund, PMC6153151).",
    FC['medical']
))

medical_ops.append(make_op(
    "Medicaid & Benefits Enrollment Drive",
    MEDICAL,
    {'medical_budget':140.0},
    {'pop_chronic': lambda ns: (setattr(ns,'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,7))) or f"chronic -{percent_of(ns.pop_chronic,7)}"), 'policy_momentum':1.2},
    "Benefits enrollment links reduce health-related homelessness pathways (HSRI/SAMHSA studies).",
    FC['medical']
))

medical_ops.append(make_op(
    "Substance Use Treatment Expansion",
    MEDICAL,
    {'medical_budget':260.0},
    {'pop_chronic': lambda ns: (setattr(ns,'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,12))) or f"chronic -{percent_of(ns.pop_chronic,12)}"), 'public_support':-1.0, 'policy_momentum':2.8},
    "Substance use treatment reduces chronic homelessness but may cause political backlash (PMC & HSRI evidence).",
    FC['medical']
))

medical_ops.append(make_op(
    "Medical Respite & Recovery Beds",
    MEDICAL,
    {'medical_budget':220.0},
    {'shelter_capacity': 80, 'pop_chronic': lambda ns: (setattr(ns,'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,5))) or f"chronic -{percent_of(ns.pop_chronic,5)}")},
    "Medical respite reduces readmissions and helps housing transitions (Commonwealth Fund case study).",
    FC['medical']
))

medical_ops.append(make_op(
    "Behavioral Health Outreach Teams",
    MEDICAL,
    {'medical_budget':180.0},
    {'outreach_teams':2, 'pop_youth': lambda ns: (setattr(ns,'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth,8))) or f"youth -{percent_of(ns.pop_youth,8)}"), 'policy_momentum':1.3},
    "Behavioral health outreach links people to services and improves long-term outcomes (HSRI/SAMHSA).",
    FC['medical']
))

medical_ops.append(make_op(
    "Hospital Discharge Coordination",
    MEDICAL,
    {'medical_budget':100.0},
    {'pop_chronic': lambda ns: (setattr(ns,'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,3))) or f"chronic -{percent_of(ns.pop_chronic,3)}"), 'public_support':0.7},
    "Coordinating discharge prevents hospital-to-street discharges and reduces inflow (Commonwealth Fund).",
    FC['medical']
))

medical_ops.append(make_op(
    "Expand Telehealth for Unhoused",
    MEDICAL,
    {'medical_budget':70.0},
    {'policy_momentum':0.6, 'public_support':0.5},
    "Telehealth increases continuity of care for hard-to-reach populations (medical outreach literature).",
    FC['medical']
))

medical_ops.append(make_op(
    "Create Medical-Legal Partnerships",
    MEDICAL,
    {'medical_budget':90.0},
    {'legal_pressure': -1.5, 'policy_momentum': 0.7},
    "Medical-legal partnerships help address root causes like eviction (spec/legal-health references).",
    FC['medical']
))

medical_ops.append(make_op(
    "Partner with Shelters for Onsite Clinics",
    MEDICAL,
    {'medical_budget':120.0},
    {'medical_vans':1, 'pop_chronic': lambda ns: (setattr(ns,'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,4))) or f"chronic -{percent_of(ns.pop_chronic,4)}")},
    "Onsite clinic partnerships increase linkage to housing and health services (PMC studies).",
    FC['medical']
))

medical_ops.append(make_op(
    "Performance-based Funding for Treatment Outcomes",
    MEDICAL,
    {'medical_budget':200.0},
    {'policy_momentum':1.8, 'public_support': -0.8},
    "Outcome-based funding can drive better program performance but causes short-term friction (funding literature).",
    FC['medical']
))

medical_ops.append(make_op(
    "Veterans Health Focus",
    MEDICAL,
    {'medical_budget':130.0},
    {'pop_veterans': lambda ns: (setattr(ns,'pop_veterans', max(0, ns.pop_veterans - percent_of(ns.pop_veterans,10))) or f"veterans -{percent_of(ns.pop_veterans,10)}"), 'policy_momentum':1.0},
    "Targeted veteran health interventions show sizeable reductions in veteran homelessness (VA/PMC).",
    FC['medical']
))

medical_ops.append(make_op(
    "Evaluation of Health Interventions (data)",
    MEDICAL,
    {'medical_budget':60.0, 'university_budget': 40.0},
    {'policy_momentum':1.4, 'public_support': 0.6},
    "Rigorous evaluation increases long-term effectiveness (HSRI/university evidence).",
    FC['medical']
))

# ---- UNIVERSITY (12 operators) ----
uni_ops = []

uni_ops.append(make_op(
    "Research & Program Evaluation",
    UNIVERSITY,
    {'university_budget': 80.0},
    {'policy_momentum': 1.5},
    "University evaluation strengthens interventions (PMC1525292, USICH evidence).",
    FC['university']
))

uni_ops.append(make_op(
    "Service-Learning & Workforce Integration",
    UNIVERSITY,
    {'university_budget': 90.0},
    {'social_workers': 5, 'pop_youth': lambda ns: (setattr(ns,'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth,10))) or f"youth -{percent_of(ns.pop_youth,10)}"), 'public_support': 1.2},
    "Students & service-learning expand capacity and reduce youth homelessness (spec resources).",
    FC['university']
))

uni_ops.append(make_op(
    "Housing Innovation Lab (modular units)",
    UNIVERSITY,
    {'university_budget': 200.0},
    {'transitional_units': 70, 'pop_chronic': lambda ns: (setattr(ns,'pop_chronic', max(0, ns.pop_chronic - percent_of(ns.pop_chronic,3))) or f"chronic -{percent_of(ns.pop_chronic,3)}"), 'policy_momentum': 2.0},
    "University-led pilots can create modular units and build evidence (spec/hilton foundation references).",
    FC['university']
))

uni_ops.append(make_op(
    "Reputation Management (PR)",
    UNIVERSITY,
    {'university_budget': 60.0},
    {'public_support': 0.6, 'policy_momentum': -0.4},
    "Universities sometimes manage reputation; can increase public support but reduce transparency (spec).",
    FC['university']
))

uni_ops.append(make_op(
    "Open Data & Dashboard (public transparency)",
    UNIVERSITY,
    {'university_budget': 50.0},
    {'policy_momentum': 0.8, 'public_support': 0.5},
    "Open data increases accountability and helps coordinate services (USICH & HUD evidence).",
    FC['university']
))

uni_ops.append(make_op(
    "Student Outreach & Volunteer Corps",
    UNIVERSITY,
    {'university_budget': 70.0},
    {'outreach_teams': 2, 'pop_youth': lambda ns: (setattr(ns,'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth,6))) or f"youth -{percent_of(ns.pop_youth,6)}"), 'public_support': 1.0},
    "Student volunteers expand reach and support programs (spec resources).",
    FC['university']
))

uni_ops.append(make_op(
    "Policy Incubator with City (pilot)",
    UNIVERSITY,
    {'university_budget': 160.0, 'neighborhood_budget': 40.0},
    {'permanent_units': 30, 'policy_momentum': 1.6},
    "Pilot incubators can produce scalable solutions (university-city collaborations documented in spec).",
    FC['university']
))

uni_ops.append(make_op(
    "Deploy Evaluation Fellows to Shelters",
    UNIVERSITY,
    {'university_budget': 90.0},
    {'social_workers': 2, 'policy_momentum': 1.0},
    "Fellows increase evaluation capacity and improve program learning (spec).",
    FC['university']
))

uni_ops.append(make_op(
    "Community-engaged Research on Displacement",
    UNIVERSITY,
    {'university_budget': 120.0},
    {'policy_momentum': 1.8, 'public_support': 0.5},
    "Community-engaged research rebuilds trust and informs anti-displacement policy (PMC1525292).",
    FC['university']
))

uni_ops.append(make_op(
    "Leverage Philanthropy for PSH",
    UNIVERSITY,
    {'university_budget': 200.0},
    {'permanent_units': 50, 'policy_momentum': 1.2},
    "Philanthropy + universities can catalyze PSH expansion (Hilton Foundation eval.).",
    FC['university']
))

uni_ops.append(make_op(
    "Student-led Rapid Rehousing Pilot",
    UNIVERSITY,
    {'university_budget': 100.0},
    {'transitional_units': 40, 'pop_youth': lambda ns: (setattr(ns,'pop_youth', max(0, ns.pop_youth - percent_of(ns.pop_youth,8))) or f"youth -{percent_of(ns.pop_youth,8)}")},
    "Student-run rapid rehousing pilots can show rapid gains for youth (case studies).",
    FC['university']
))

uni_ops.append(make_op(
    "Academic Advocacy Campaign",
    UNIVERSITY,
    {'university_budget': 60.0},
    {'public_support': 0.9, 'policy_momentum': 0.6},
    "Academic advocacy helps shift city policy to evidence-based approaches (USICH / NLIHC evidence).",
    FC['university']
))

# Aggregate operators
SHELTERS_OPS = shelters_ops
NEIGHBOR_OPS = neighbor_ops
BUSINESS_OPS = business_ops
MEDICAL_OPS = medical_ops
UNIVERSITY_OPS = uni_ops

OPERATORS = SHELTERS_OPS + NEIGHBOR_OPS + BUSINESS_OPS + MEDICAL_OPS + UNIVERSITY_OPS

# INITIAL STATE
def create_initial_state():
    s = State()
    s.recalc_population()
    s.record_trend()
    return s

# ROLES meta (for Select_Roles)
ROLES = ROLES_List([
    {'name': 'Neighborhoods', 'min': 1, 'max': 1},
    {'name': 'Business', 'min': 1, 'max': 1},
    {'name': 'Medical', 'min': 1, 'max': 1},
    {'name': 'SheltersServices', 'min': 1, 'max': 1},
    {'name': 'University', 'min': 1, 'max': 1},
    {'name': 'Observer', 'min': 0, 'max': 20}
])
ROLES.min_num_of_roles_to_play = 5
ROLES.max_num_of_roles_to_play = 25

# STATE_VIS hook
BRIFL_SVG = True
render_state = None
def use_BRIFL_SVG():
    global render_state
    from CityWithoutWalls_SVG_VIS_FOR_BRIFL import render_state
