'''
CityWithoutWalls.py
Educational strategy game simulating urban homelessness as a wicked problem.
Players assume different stakeholder roles to collectively address a homelessness crisis.
Works with Web_SOLUZION5 system.
'''

#<METADATA>
SOLUZION_VERSION = "5.0"
PROBLEM_NAME = "City Without Walls"
PROBLEM_VERSION = "1.0"
PROBLEM_AUTHORS = ['Educational Simulation Team']
PROBLEM_CREATION_DATE = "10-November-2025"
PROBLEM_DESC=\
 '''City Without Walls simulates the complexity of addressing urban homelessness.
 Five stakeholder roles (Neighborhoods, Business District, Medical Quarter, 
 Shelters/Services, University) must balance competing interests and limited resources
 to reduce homelessness by 15% while maintaining public support and system health.
 Features comprehensive state tracking, evidence-based interventions, and ethical dilemmas.'''
#</METADATA>

#<COMMON_DATA>
NEIGHBORHOODS = 0
BUSINESS = 1
MEDICAL = 2
SHELTERS = 3
UNIVERSITY = 4
OBSERVER = 5

NAMES = ["Neighborhoods Coalition", "Business District Association", 
         "Medical Quarter Consortium", "Shelters & Services Network",
         "University Consortium", "Observer"]

SEASONS = ["Winter", "Spring", "Summer", "Fall"]
#</COMMON_DATA>

#<COMMON_CODE>
DEBUG = False
from soluzion5 import Basic_State, \
  Basic_Operator as Operator, ROLES_List, add_to_next_transition
import Select_Roles as sr
import random

def int_to_name(i):
    return NAMES[i]

class State(Basic_State):
    def __init__(self, old=None):
        if old is None:
            # Initial state
            self.whose_turn = NEIGHBORHOODS
            self.current_role_num = NEIGHBORHOODS
            self.current_role = int_to_name(self.current_role_num)
            
            # Global metrics
            self.turn = 1
            self.homeless_population = 10700  # Total homeless
            self.unsheltered = 4500
            self.sheltered = 3800
            self.transitional = 2400
            self.at_risk_population = 38000
            self.public_support = 50  # percentage
            self.government_budget = 1200000  # per turn allocation
            
            # System health metrics
            self.trust_index = 42
            self.stigma_index = 68
            self.service_coordination = 35
            self.housing_affordability = 38.5  # rent as % of income
            
            # Neighborhoods Coalition
            self.neigh_budget = 750000
            self.neigh_influence = 65
            self.property_value_index = 100
            self.safety_perception = 45
            self.complaint_rate = 22
            
            # Business District
            self.biz_budget = 900000
            self.biz_influence = 70
            self.customer_traffic = 100
            self.cleanliness_index = 52
            self.revenue_impact = 0
            self.biz_reputation = 50
            
            # Medical Quarter
            self.med_budget = 600000
            self.med_influence = 55
            self.clinic_capacity = 240
            self.patient_volume = 190
            self.health_outcome_index = 38
            self.staff_burnout = 30
            
            # Shelters & Services
            self.shelter_budget = 500000
            self.shelter_influence = 50
            self.bed_capacity = 3800
            self.occupancy_rate = 100
            self.volunteer_count = 280
            self.waitlist = 420
            self.housing_placements = 0
            
            # University
            self.uni_budget = 400000
            self.uni_influence = 45
            self.research_funding = 120000
            self.reputation_score = 75
            self.community_engagement = 40
            self.publications = 0
            
            # Tracking variables
            self.season_index = 0  # 0=Winter, 1=Spring, 2=Summer, 3=Fall
            self.homeless_deaths = 0
            self.human_cost_index = 0  # Ethical tracking
            self.sweeps_conducted = 0
            self.last_positive_action = True
            self.pilot_active = False
            self.research_projects = []
            
            self.win = ""
            self.winner = -1
            
        else:
            # Deep copy from old state
            self.whose_turn = old.whose_turn
            self.current_role = old.current_role
            self.current_role_num = old.current_role_num
            self.turn = old.turn
            self.homeless_population = old.homeless_population
            self.unsheltered = old.unsheltered
            self.sheltered = old.sheltered
            self.transitional = old.transitional
            self.at_risk_population = old.at_risk_population
            self.public_support = old.public_support
            self.government_budget = old.government_budget
            self.trust_index = old.trust_index
            self.stigma_index = old.stigma_index
            self.service_coordination = old.service_coordination
            self.housing_affordability = old.housing_affordability
            self.neigh_budget = old.neigh_budget
            self.neigh_influence = old.neigh_influence
            self.property_value_index = old.property_value_index
            self.safety_perception = old.safety_perception
            self.complaint_rate = old.complaint_rate
            self.biz_budget = old.biz_budget
            self.biz_influence = old.biz_influence
            self.customer_traffic = old.customer_traffic
            self.cleanliness_index = old.cleanliness_index
            self.revenue_impact = old.revenue_impact
            self.biz_reputation = old.biz_reputation
            self.med_budget = old.med_budget
            self.med_influence = old.med_influence
            self.clinic_capacity = old.clinic_capacity
            self.patient_volume = old.patient_volume
            self.health_outcome_index = old.health_outcome_index
            self.staff_burnout = old.staff_burnout
            self.shelter_budget = old.shelter_budget
            self.shelter_influence = old.shelter_influence
            self.bed_capacity = old.bed_capacity
            self.occupancy_rate = old.occupancy_rate
            self.volunteer_count = old.volunteer_count
            self.waitlist = old.waitlist
            self.housing_placements = old.housing_placements
            self.uni_budget = old.uni_budget
            self.uni_influence = old.uni_influence
            self.research_funding = old.research_funding
            self.reputation_score = old.reputation_score
            self.community_engagement = old.community_engagement
            self.publications = old.publications
            self.season_index = old.season_index
            self.homeless_deaths = old.homeless_deaths
            self.human_cost_index = old.human_cost_index
            self.sweeps_conducted = old.sweeps_conducted
            self.last_positive_action = old.last_positive_action
            self.pilot_active = old.pilot_active
            self.research_projects = old.research_projects[:]
            self.win = old.win
            self.winner = old.winner

    def __str__(self):
        season = SEASONS[self.season_index]
        txt = f"=== CITY WITHOUT WALLS - Turn {self.turn} ({season}) ===\n"
        txt += f"Current Player: {self.current_role}\n\n"
        txt += f"CITYWIDE METRICS:\n"
        txt += f"Total Homeless: {self.homeless_population} (Goal: 9,095)\n"
        txt += f"  - Unsheltered: {self.unsheltered}\n"
        txt += f"  - Sheltered: {self.sheltered}\n"
        txt += f"  - Transitional: {self.transitional}\n"
        txt += f"At-Risk Population: {self.at_risk_population}\n"
        txt += f"Public Support: {self.public_support}%\n"
        txt += f"Trust Index: {self.trust_index}/100\n"
        txt += f"Service Coordination: {self.service_coordination}%\n\n"
        txt += f"STAKEHOLDER STATUS:\n"
        txt += f"Neighborhoods: ${self.neigh_budget:,} budget, {self.neigh_influence} influence\n"
        txt += f"  Property Values: {self.property_value_index}, Safety: {self.safety_perception}\n"
        txt += f"Business: ${self.biz_budget:,} budget, {self.biz_influence} influence\n"
        txt += f"  Traffic: {self.customer_traffic}, Cleanliness: {self.cleanliness_index}\n"
        txt += f"Medical: ${self.med_budget:,} budget, {self.med_influence} influence\n"
        txt += f"  Health Index: {self.health_outcome_index}, Burnout: {self.staff_burnout}%\n"
        txt += f"Shelters: ${self.shelter_budget:,} budget, {self.shelter_influence} influence\n"
        txt += f"  Beds: {self.bed_capacity}, Waitlist: {self.waitlist}\n"
        txt += f"University: ${self.uni_budget:,} budget, {self.uni_influence} influence\n"
        txt += f"  Reputation: {self.reputation_score}, Engagement: {self.community_engagement}\n"
        return txt

    def __eq__(self, s):
        return self.__str__() == s.__str__()

    def __hash__(self):
        return (self.__str__()).__hash__()
    
    def find_any_win(self):
        # Catastrophic failures
        if self.homeless_deaths > 50:
            return ("HUMANITARIAN CRISIS: More than 50 homeless deaths this season. Game over.\n\n"
                   "In real cities, winter weather and inadequate shelter capacity lead to preventable deaths. "
                   "This tragedy underscores the urgency of evidence-based housing interventions.", -1)
        
        if self.public_support < 25 and self.turn > 6:
            return ("POLITICAL COLLAPSE: Public support has fallen below 25%. The coalition has lost "
                   "political viability. Game over.\n\n"
                   "Public trust is essential for sustainable policy. When communities lose faith in "
                   "interventions, funding disappears and programs fail.", -1)
        
        # Check if game complete (turn 24)
        if self.turn > 24:
            reduction = (10700 - self.homeless_population) / 10700 * 100
            
            if self.homeless_population <= 8560 and self.public_support > 55:
                return (f"EXEMPLARY SUCCESS: Reduced homelessness by {reduction:.1f}% (target: 20%) while "
                       f"maintaining strong public support.\n\n"
                       f"You achieved systemic change through evidence-based interventions and collaborative "
                       f"governance. Housing placements: {self.housing_placements}. Trust Index: {self.trust_index}. "
                       f"This represents what's possible when communities prioritize dignity and evidence over "
                       f"punitive approaches.", 1)
            
            elif self.homeless_population <= 9095 and self.public_support > 45:
                return (f"SUCCESS: Reduced homelessness by {reduction:.1f}% (target: 15%) with adequate "
                       f"public support.\n\n"
                       f"Meaningful progress achieved. Housing placements: {self.housing_placements}. "
                       f"The work continues - homelessness is a wicked problem requiring sustained commitment.", 1)
            
            elif self.homeless_population <= 9630:
                return (f"PARTIAL SUCCESS: Reduced homelessness by {reduction:.1f}% (5-10% reduction).\n\n"
                       f"Some progress, but fell short of goals. Consider: Were interventions evidence-based? "
                       f"Did stakeholders coordinate effectively? Human Cost Index: {self.human_cost_index}.", 0)
            
            elif self.homeless_population < 10700:
                return (f"MINIMAL PROGRESS: Reduced homelessness by only {reduction:.1f}%.\n\n"
                       f"The wicked problem resisted your interventions. Reflect on what approaches might "
                       f"have been more effective. Real cities face these challenges continuously.", 0)
            
            else:
                return (f"FAILURE: Homelessness increased to {self.homeless_population} (from 10,700).\n\n"
                       f"This outcome reflects how punitive approaches, lack of coordination, and inadequate "
                       f"investment worsen homelessness. Human Cost Index: {self.human_cost_index}.", -1)
        
        return False
    
    def check_for_win(self):
        any_win = self.find_any_win()
        if any_win:
            (self.win, self.winner) = any_win
        return any_win
    
    def is_goal(self):
        any_win = self.check_for_win()
        if any_win:
            return True
        return False

    def goal_message(self):
        if self.win != "":
            return self.win
        else:
            return f"Turn {self.turn}/24: Continue working toward 15% reduction in homelessness."

    def text_view_for_role(self, role_num):
        role_name = int_to_name(role_num)
        txt = f"Current view for {role_name}:\n"
        txt += str(self)
        
        if self.win == "" and not self.is_goal():
            txt += f"\nIt's {int_to_name(self.whose_turn)}'s turn.\n"
        elif self.winner != -1:
            txt += f"\nWinner: {int_to_name(self.winner)}\n"
        elif self.win != "":
            txt += self.win + "\n"
        
        # Role-specific information
        if self.win == "":
            if role_num == NEIGHBORHOODS:
                txt += "\n--- NEIGHBORHOODS COALITION GOALS ---\n"
                txt += f"Maintain Property Values > 95 (currently {self.property_value_index})\n"
                txt += f"Reduce visible homelessness in residential zones by 30%\n"
                txt += f"Keep Safety Perception > 60 (currently {self.safety_perception})\n"
                if self.complaint_rate > 30:
                    txt += f"WARNING: High complaint rate ({self.complaint_rate}/month)\n"
            
            elif role_num == BUSINESS:
                txt += "\n--- BUSINESS DISTRICT GOALS ---\n"
                txt += f"Maintain Customer Traffic > 95 (currently {self.customer_traffic})\n"
                txt += f"Keep Cleanliness Index > 75 (currently {self.cleanliness_index})\n"
                txt += f"Revenue Impact > -$200K (currently ${self.revenue_impact:,})\n"
                if self.cleanliness_index < 55:
                    txt += "WARNING: Cleanliness concerns affecting business\n"
            
            elif role_num == MEDICAL:
                txt += "\n--- MEDICAL QUARTER GOALS ---\n"
                txt += f"Improve Health Index to 65+ (currently {self.health_outcome_index})\n"
                txt += f"Treat at least 400 unique patients (progress tracked internally)\n"
                txt += f"Keep Staff Burnout < 50% (currently {self.staff_burnout}%)\n"
                if self.staff_burnout > 60:
                    txt += "WARNING: Staff burnout critical!\n"
            
            elif role_num == SHELTERS:
                txt += "\n--- SHELTERS & SERVICES GOALS ---\n"
                txt += f"Reduce Waitlist to < 150 (currently {self.waitlist})\n"
                txt += f"Increase Bed Capacity by 30% (currently {self.bed_capacity}, started at 3,800)\n"
                txt += f"Achieve 400+ Housing Placements (currently {self.housing_placements})\n"
                if self.waitlist > 500:
                    txt += "CRISIS: Waitlist exceeds capacity!\n"
            
            elif role_num == UNIVERSITY:
                txt += "\n--- UNIVERSITY CONSORTIUM GOALS ---\n"
                txt += f"Publish 3 research findings (currently {self.publications})\n"
                txt += f"Maintain Reputation > 70 (currently {self.reputation_score})\n"
                txt += f"Community Engagement > 65 (currently {self.community_engagement})\n"
                if self.reputation_score < 65:
                    txt += "WARNING: Reputation at risk\n"
        
        return txt

SESSION = None

def next_player(k):
    if k == NEIGHBORHOODS: return BUSINESS
    elif k == BUSINESS: return MEDICAL
    elif k == MEDICAL: return SHELTERS
    elif k == SHELTERS: return UNIVERSITY
    else: return NEIGHBORHOODS

def whose_move(state):
    '''Returns whose move it is (required by some SOLUZION5 versions)'''
    return state.whose_turn

def describe_move(old_state, new_state):
    '''Describe what happened in this move (for transition messages)'''
    role_name = int_to_name(old_state.whose_turn)
    return f"{role_name} completed their action. Now it's {int_to_name(new_state.whose_turn)}'s turn."

def update_turn(news):
    # Apply decay effects
    if not news.last_positive_action:
        news.public_support = clamp(news.public_support - 1, 0, 100)
    
    # Seasonal effects - only apply when changing players within same round
    apply_seasonal_effects(news)
    
    # Volunteer attrition - check every 4 player turns
    turn_count = (news.turn - 1) * 5 + (news.whose_turn + 1)
    if turn_count % 4 == 0:
        news.volunteer_count = int(news.volunteer_count * 0.95)
    
    # Staff burnout increase if overworked
    if news.patient_volume > news.clinic_capacity * 0.9:
        news.staff_burnout = clamp(news.staff_burnout + 8, 0, 100)
    
    current = news.whose_turn
    updated = next_player(current)
    news.whose_turn = updated
    news.current_role_num = updated
    news.current_role = NAMES[updated]
    
    # Every full round (5 turns), increment turn counter and update season
    if updated == NEIGHBORHOODS:
        news.turn += 1
        news.last_positive_action = False
        # Update season every 3 rounds
        if news.turn % 3 == 0:
            news.season_index = (news.season_index + 1) % 4

def apply_seasonal_effects(s):
    season = SEASONS[s.season_index]
    
    if season == "Winter":
        # Increase mortality risk for unsheltered
        if s.unsheltered > 3000:
            deaths = int(s.unsheltered * 0.002)  # 0.2% mortality
            s.homeless_deaths += deaths
            if deaths > 0:
                add_to_next_transition(f"Winter conditions: {deaths} homeless deaths reported.", s)
        
        # Increased shelter demand
        demand_increase = int(s.unsheltered * 0.15)
        s.waitlist = clamp(s.waitlist + demand_increase // 10, 0, 5000)
    
    elif season == "Summer":
        # Heat-related health risks
        if s.health_outcome_index < 45:
            s.health_outcome_index = clamp(s.health_outcome_index - 2, 0, 100)

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def get_session():
    return SESSION

#------------------
# NEIGHBORHOODS COALITION OPERATORS
#------------------

def launch_media_campaign(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} launches 'Community Voices for Safe Streets' campaign.", new_s)
    
    new_s.neigh_budget -= 100000
    new_s.neigh_influence -= 10
    new_s.public_support = clamp(s.public_support + 8, 0, 100)
    add_to_next_transition(f"Public support increased to {new_s.public_support}%.", new_s)
    
    new_s.stigma_index = clamp(s.stigma_index + 5, 0, 100)
    add_to_next_transition("Media campaign increases stigma through negative framing.", new_s)
    
    new_s.homeless_population = int(s.homeless_population * 0.99)
    new_s.unsheltered = int(new_s.unsheltered * 0.99)
    add_to_next_transition(f"Indirect reduction: {s.homeless_population - new_s.homeless_population} people (government response).", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def fund_private_security(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} funds private security patrols in residential zones.", new_s)
    
    new_s.neigh_budget -= 75000
    new_s.neigh_influence -= 15
    new_s.safety_perception = clamp(s.safety_perception + 12, 0, 100)
    add_to_next_transition(f"Safety perception increased to {new_s.safety_perception}.", new_s)
    
    # Displacement effect
    displaced = int(new_s.unsheltered * 0.15)
    new_s.unsheltered = new_s.unsheltered - displaced
    add_to_next_transition(f"Visible homelessness reduced by {displaced} (displaced to other zones).", new_s)
    
    new_s.trust_index = clamp(s.trust_index - 10, 0, 100)
    add_to_next_transition(f"Trust index decreased to {new_s.trust_index} due to enforcement.", new_s)
    
    new_s.public_support = clamp(s.public_support - 5, 0, 100)
    add_to_next_transition("Public support decreased (concerns about militarization).", new_s)
    
    new_s.property_value_index = clamp(s.property_value_index + 2, 0, 150)
    new_s.human_cost_index += 8
    
    update_turn(new_s)
    return new_s

def sponsor_outreach_program(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} sponsors 'Neighborhood Ambassadors' outreach program.", new_s)
    
    new_s.neigh_budget -= 60000
    new_s.neigh_influence -= 8
    new_s.trust_index = clamp(s.trust_index + 6, 0, 100)
    add_to_next_transition(f"Trust index increased to {new_s.trust_index}.", new_s)
    
    new_s.volunteer_count = int(s.volunteer_count * 1.09)
    add_to_next_transition(f"Volunteer count increased to {new_s.volunteer_count}.", new_s)
    
    # Connection to services
    connected = int(s.unsheltered * 0.12)
    new_s.unsheltered -= connected
    new_s.sheltered += connected
    add_to_next_transition(f"{connected} people connected to services.", new_s)
    
    new_s.public_support = clamp(s.public_support + 3, 0, 100)
    new_s.property_value_index = clamp(s.property_value_index + 1, 0, 150)
    new_s.service_coordination = clamp(s.service_coordination + 5, 0, 100)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def host_community_forums(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} hosts community forums for dialogue.", new_s)
    
    new_s.neigh_budget -= 15000
    new_s.neigh_influence -= 5
    new_s.complaint_rate = max(0, s.complaint_rate - 8)
    add_to_next_transition(f"Complaint rate decreased to {new_s.complaint_rate}/month.", new_s)
    
    new_s.public_support = clamp(s.public_support + 2, 0, 100)
    new_s.service_coordination = clamp(s.service_coordination + 3, 0, 100)
    new_s.stigma_index = clamp(s.stigma_index - 3, 0, 100)
    add_to_next_transition("Community understanding improved through dialogue.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

#------------------
# BUSINESS DISTRICT OPERATORS
#------------------

def partner_city_sweeps(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} partners with city sanitation for encampment sweeps.", new_s)
    
    new_s.biz_budget -= 120000
    new_s.biz_influence -= 12
    new_s.cleanliness_index = clamp(s.cleanliness_index + 18, 0, 100)
    add_to_next_transition(f"Cleanliness index increased to {new_s.cleanliness_index}.", new_s)
    
    new_s.customer_traffic = clamp(s.customer_traffic + 6, 0, 150)
    
    # Temporary displacement
    displaced = int(new_s.unsheltered * 0.20)
    add_to_next_transition(f"{displaced} people displaced from downtown (temporary effect).", new_s)
    
    # Major trust damage
    new_s.trust_index = clamp(s.trust_index - 15, 0, 100)
    add_to_next_transition(f"Trust index severely damaged: {new_s.trust_index}.", new_s)
    
    new_s.public_support = clamp(s.public_support - 8, 0, 100)
    add_to_next_transition("Public backlash from belongings destruction.", new_s)
    
    new_s.sweeps_conducted += 1
    new_s.human_cost_index += 15
    
    add_to_next_transition("Reality check: Encampment sweeps disperse people without reducing homelessness.", new_s)
    
    update_turn(new_s)
    return new_s

def fund_job_readiness(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} funds 'Pathways to Work' job readiness program.", new_s)
    
    new_s.biz_budget -= 180000
    new_s.biz_influence -= 8
    new_s.public_support = clamp(s.public_support + 6, 0, 100)
    add_to_next_transition(f"Public support increased to {new_s.public_support}%.", new_s)
    
    new_s.biz_reputation = clamp(s.biz_reputation + 8, 0, 100)
    
    # Employment impact (delayed, reduced homelessness)
    employed = int(s.homeless_population * 0.025)
    new_s.homeless_population -= employed
    new_s.transitional -= employed // 2
    new_s.sheltered -= employed // 2
    add_to_next_transition(f"{employed} people gained employment, exited homelessness.", new_s)
    
    # Prevention
    new_s.at_risk_population = int(s.at_risk_population * 0.97)
    add_to_next_transition(f"At-risk population reduced to {new_s.at_risk_population}.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def deploy_street_ambassadors(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} deploys volunteer street ambassadors.", new_s)
    
    new_s.biz_budget -= 90000
    new_s.biz_influence -= 6
    new_s.volunteer_count += 40
    add_to_next_transition(f"Volunteer count increased to {new_s.volunteer_count}.", new_s)
    
    new_s.trust_index = clamp(s.trust_index + 8, 0, 100)
    add_to_next_transition(f"Trust index increased to {new_s.trust_index}.", new_s)
    
    # Service connections
    connected = int(s.unsheltered * 0.18)
    new_s.unsheltered -= connected
    new_s.sheltered += min(connected, new_s.waitlist)
    new_s.waitlist = max(0, new_s.waitlist - connected // 2)
    add_to_next_transition(f"{connected} people connected to services.", new_s)
    
    new_s.biz_reputation = clamp(s.biz_reputation + 6, 0, 100)
    new_s.cleanliness_index = clamp(s.cleanliness_index + 8, 0, 100)
    new_s.service_coordination = clamp(s.service_coordination + 4, 0, 100)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def support_affordable_housing(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} supports mixed-income affordable housing development.", new_s)
    
    new_s.biz_budget -= 350000
    new_s.biz_influence -= 25
    new_s.public_support = clamp(s.public_support + 12, 0, 100)
    add_to_next_transition(f"Public support increased to {new_s.public_support}% (major goodwill).", new_s)
    
    new_s.biz_reputation = clamp(s.biz_reputation + 15, 0, 100)
    add_to_next_transition(f"Business reputation increased to {new_s.biz_reputation} (legacy impact).", new_s)
    
    # Housing units (delayed, will be available in 4 turns)
    add_to_next_transition("85 affordable housing units under construction (available in 4 turns).", new_s)
    
    new_s.at_risk_population = int(s.at_risk_population * 0.94)
    add_to_next_transition(f"At-risk population reduced to {new_s.at_risk_population}.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

#------------------
# MEDICAL QUARTER OPERATORS
#------------------

def open_health_clinic(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} opens low-barrier health clinic.", new_s)
    
    new_s.med_budget -= 200000
    new_s.med_influence -= 10
    new_s.clinic_capacity += 120
    add_to_next_transition(f"Clinic capacity increased to {new_s.clinic_capacity} patients/month.", new_s)
    
    new_s.health_outcome_index = clamp(s.health_outcome_index + 12, 0, 100)
    add_to_next_transition(f"Health outcome index improved to {new_s.health_outcome_index}.", new_s)
    
    new_s.patient_volume = min(new_s.clinic_capacity, s.patient_volume + 80)
    
    # Health stability enables housing stability
    housed = int(s.homeless_population * 0.03)
    new_s.homeless_population -= housed
    new_s.sheltered -= housed // 2
    new_s.unsheltered -= housed // 2
    add_to_next_transition(f"{housed} people achieved housing stability through health improvements.", new_s)
    
    new_s.public_support = clamp(s.public_support + 5, 0, 100)
    new_s.staff_burnout = clamp(s.staff_burnout - 5, 0, 100)
    new_s.at_risk_population = int(s.at_risk_population * 0.98)
    
    add_to_next_transition("Evidence: Low-barrier clinics improve health outcomes and enable housing stability.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def launch_mental_health_services(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} launches integrated mental health & addiction services.", new_s)
    
    new_s.med_budget -= 280000
    new_s.med_influence -= 15
    new_s.health_outcome_index = clamp(s.health_outcome_index + 18, 0, 100)
    add_to_next_transition(f"Health outcome index significantly improved to {new_s.health_outcome_index}.", new_s)
    
    # Mental health treatment
    new_s.patient_volume = min(new_s.clinic_capacity, s.patient_volume + 100)
    
    # Addresses root causes - significant long-term impact
    reduction = int(s.homeless_population * 0.04)
    new_s.homeless_population -= reduction
    new_s.transitional -= reduction // 2
    new_s.sheltered -= reduction // 2
    add_to_next_transition(f"{reduction} people successfully housed through mental health support.", new_s)
    
    new_s.public_support = clamp(s.public_support + 7, 0, 100)
    new_s.service_coordination = clamp(s.service_coordination + 6, 0, 100)
    
    add_to_next_transition("Evidence: Mental health services increase housing retention by 35% when paired with stable housing.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def establish_medical_respite(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} establishes medical respite care facility.", new_s)
    
    new_s.med_budget -= 160000
    new_s.med_influence -= 15
    new_s.bed_capacity += 45
    add_to_next_transition(f"Medical respite beds added: {new_s.bed_capacity} total beds.", new_s)
    
    new_s.health_outcome_index = clamp(s.health_outcome_index + 10, 0, 100)
    add_to_next_transition(f"Health outcomes improved to {new_s.health_outcome_index}.", new_s)
    
    # Medical stability pathway to housing
    housed = int(s.homeless_population * 0.02)
    new_s.homeless_population -= housed
    new_s.sheltered -= housed
    add_to_next_transition(f"{housed} people transitioned to housing through medical respite.", new_s)
    
    new_s.public_support = clamp(s.public_support + 4, 0, 100)
    new_s.service_coordination = clamp(s.service_coordination + 5, 0, 100)
    
    add_to_next_transition("Evidence: Medical respite reduces hospital readmissions by 32% and offers pathway to housing.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def mobile_outreach_medicine(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} launches mobile outreach and street medicine program.", new_s)
    
    new_s.med_budget -= 95000
    new_s.med_influence -= 8
    new_s.trust_index = clamp(s.trust_index + 12, 0, 100)
    add_to_next_transition(f"Trust index increased to {new_s.trust_index} (meets people where they are).", new_s)
    
    new_s.health_outcome_index = clamp(s.health_outcome_index + 6, 0, 100)
    
    # Reaches unsheltered population
    treated = int(s.unsheltered * 0.15)
    add_to_next_transition(f"{treated} unsheltered individuals received healthcare.", new_s)
    
    # Some transition to services
    connected = int(s.unsheltered * 0.08)
    new_s.unsheltered -= connected
    new_s.sheltered += connected
    add_to_next_transition(f"{connected} people connected to shelter services.", new_s)
    
    new_s.public_support = clamp(s.public_support + 3, 0, 100)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

#------------------
# SHELTERS & SERVICES OPERATORS
#------------------

def volunteer_recruitment_drive(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} launches 'Be the Change' volunteer recruitment drive.", new_s)
    
    new_s.shelter_budget -= 50000
    new_s.shelter_influence -= 5
    new_s.volunteer_count = int(s.volunteer_count * 1.10)
    add_to_next_transition(f"Volunteer count increased to {new_s.volunteer_count}.", new_s)
    
    # Increased service delivery
    reduction = int(s.homeless_population * 0.02)
    new_s.homeless_population -= reduction
    new_s.unsheltered -= reduction
    add_to_next_transition(f"{reduction} people helped through expanded volunteer services.", new_s)
    
    new_s.public_support = clamp(s.public_support + 5, 0, 100)
    add_to_next_transition(f"Public support increased to {new_s.public_support}%.", new_s)
    
    new_s.community_engagement = clamp(s.community_engagement + 4, 0, 100)
    new_s.staff_burnout = clamp(s.staff_burnout - 3, 0, 100)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def expand_shelter_capacity(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} expands emergency shelter capacity.", new_s)
    
    new_s.shelter_budget -= 150000
    new_s.shelter_influence -= 10
    new_s.bed_capacity += 180
    add_to_next_transition(f"Bed capacity increased to {new_s.bed_capacity} beds.", new_s)
    
    # Move unsheltered to sheltered
    sheltered = min(180, s.unsheltered, s.waitlist)
    new_s.unsheltered -= sheltered
    new_s.sheltered += sheltered
    new_s.waitlist = max(0, s.waitlist - 90)
    add_to_next_transition(f"{sheltered} people moved from streets to shelter.", new_s)
    
    new_s.public_support = clamp(s.public_support - 3, 0, 100)
    add_to_next_transition("Public support slightly decreased (concerns about enabling).", new_s)
    
    add_to_next_transition("Reality: Expanding shelter capacity reduces unsheltered temporarily but doesn't solve underlying housing crisis.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def housing_navigation_program(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} implements comprehensive housing navigation program.", new_s)
    
    new_s.shelter_budget -= 120000
    new_s.shelter_influence -= 10
    
    # Significantly improves housing placement
    placements = int(s.sheltered * 0.25)
    new_s.homeless_population -= placements
    new_s.sheltered -= placements
    new_s.housing_placements += placements
    add_to_next_transition(f"{placements} people successfully placed in permanent housing.", new_s)
    
    new_s.waitlist = max(0, s.waitlist - 60)
    add_to_next_transition(f"Waitlist reduced to {new_s.waitlist}.", new_s)
    
    new_s.public_support = clamp(s.public_support + 6, 0, 100)
    add_to_next_transition("Public support increased (solution-focused approach).", new_s)
    
    new_s.service_coordination = clamp(s.service_coordination + 8, 0, 100)
    
    add_to_next_transition("Evidence: Housing navigation reduces shelter stay length by 30% and improves retention.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def establish_psh(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} establishes Permanent Supportive Housing (Housing First model).", new_s)
    
    new_s.shelter_budget -= 400000
    new_s.shelter_influence -= 30
    
    # Major impact - targets chronically homeless
    housed = 50
    new_s.homeless_population -= housed
    new_s.sheltered -= housed // 2
    new_s.unsheltered -= housed // 2
    new_s.housing_placements += housed
    add_to_next_transition(f"{housed} chronically homeless individuals housed with wraparound services.", new_s)
    
    new_s.public_support = clamp(s.public_support + 10, 0, 100)
    add_to_next_transition(f"Public support increased to {new_s.public_support}% (evidence-based solution).", new_s)
    
    new_s.health_outcome_index = clamp(s.health_outcome_index + 8, 0, 100)
    new_s.service_coordination = clamp(s.service_coordination + 10, 0, 100)
    
    add_to_next_transition("Evidence: Housing First achieves 85-90% retention rates and reduces emergency services use by 40%.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def partner_university_research(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} partners with university for research evaluation.", new_s)
    
    new_s.shelter_budget -= 75000
    new_s.shelter_influence -= 8
    
    new_s.publications += 1
    add_to_next_transition(f"Research publication count: {new_s.publications}.", new_s)
    
    new_s.public_support = clamp(s.public_support + 4, 0, 100)
    add_to_next_transition("Public support increased (transparency and accountability).", new_s)
    
    new_s.service_coordination = clamp(s.service_coordination + 6, 0, 100)
    new_s.uni_influence = clamp(s.uni_influence + 5, 0, 100)
    new_s.reputation_score = clamp(s.reputation_score + 6, 0, 100)
    
    add_to_next_transition("Research identifies most effective interventions for future use.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

#------------------
# UNIVERSITY OPERATORS
#------------------

def student_outreach_program(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} launches student outreach and service learning program.", new_s)
    
    new_s.uni_budget -= 40000
    new_s.uni_influence -= 5
    new_s.volunteer_count += 60
    add_to_next_transition(f"Volunteer count increased to {new_s.volunteer_count} (student volunteers).", new_s)
    
    new_s.community_engagement = clamp(s.community_engagement + 12, 0, 100)
    add_to_next_transition(f"Community engagement increased to {new_s.community_engagement}.", new_s)
    
    # Service connections
    connected = int(s.unsheltered * 0.10)
    new_s.unsheltered -= connected
    new_s.sheltered += connected
    add_to_next_transition(f"{connected} people connected to services through student outreach.", new_s)
    
    new_s.public_support = clamp(s.public_support + 3, 0, 100)
    
    add_to_next_transition("Students gain empathy and understanding of systemic issues.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def conduct_policy_research(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} conducts comprehensive policy research and evaluation.", new_s)
    
    new_s.uni_budget -= 90000
    new_s.uni_influence -= 10
    new_s.publications += 1
    new_s.research_projects.append(f"Turn {s.turn} Research")
    add_to_next_transition(f"Research publication #{new_s.publications} completed.", new_s)
    
    # Increases effectiveness of all interventions
    new_s.service_coordination = clamp(s.service_coordination + 8, 0, 100)
    add_to_next_transition(f"Service coordination improved to {new_s.service_coordination}% (evidence-based practice).", new_s)
    
    # Give influence to all stakeholders
    new_s.neigh_influence = clamp(s.neigh_influence + 5, 0, 100)
    new_s.biz_influence = clamp(s.biz_influence + 5, 0, 100)
    new_s.med_influence = clamp(s.med_influence + 5, 0, 100)
    new_s.shelter_influence = clamp(s.shelter_influence + 5, 0, 100)
    add_to_next_transition("All stakeholders gain influence from evidence-based insights.", new_s)
    
    new_s.reputation_score = clamp(s.reputation_score + 8, 0, 100)
    new_s.public_support = clamp(s.public_support + 2, 0, 100)
    
    add_to_next_transition("Research reveals: Housing First reduces costs, sweeps don't reduce homelessness, coordination is critical.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def pilot_innovation_program(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} launches pilot innovative intervention (tiny homes/guaranteed income).", new_s)
    
    new_s.uni_budget -= 150000
    new_s.uni_influence -= 20
    new_s.research_funding -= 150000
    new_s.pilot_active = True
    
    # 60% chance of success
    if random.random() < 0.6:
        add_to_next_transition("PILOT SUCCESS: Innovative approach shows promising results!", new_s)
        
        housed = 40
        new_s.homeless_population -= housed
        new_s.unsheltered -= housed
        add_to_next_transition(f"{housed} people successfully housed through pilot program.", new_s)
        
        new_s.reputation_score = clamp(s.reputation_score + 12, 0, 100)
        new_s.public_support = clamp(s.public_support + 5, 0, 100)
        new_s.publications += 1
        add_to_next_transition("Research published on successful pilot intervention.", new_s)
    else:
        add_to_next_transition("Pilot encounters challenges but provides learning opportunity.", new_s)
        new_s.reputation_score = clamp(s.reputation_score - 5, 0, 100)
        add_to_next_transition("Some reputational impact from publicized challenges.", new_s)
    
    new_s.community_engagement = clamp(s.community_engagement + 8, 0, 100)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def community_academic_forums(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} hosts community-academic partnership forums.", new_s)
    
    new_s.uni_budget -= 25000
    new_s.uni_influence -= 8
    new_s.community_engagement = clamp(s.community_engagement + 15, 0, 100)
    add_to_next_transition(f"Community engagement increased to {new_s.community_engagement}.", new_s)
    
    # Improves all relationships
    new_s.service_coordination = clamp(s.service_coordination + 6, 0, 100)
    new_s.public_support = clamp(s.public_support + 3, 0, 100)
    new_s.stigma_index = clamp(s.stigma_index - 5, 0, 100)
    add_to_next_transition(f"Stigma reduced to {new_s.stigma_index} through dialogue.", new_s)
    
    add_to_next_transition("Forums create space for mutual learning between academics and community.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

def develop_data_dashboard(s):
    new_s = State(s)
    add_to_next_transition(f"{int_to_name(s.whose_turn)} develops comprehensive homelessness data dashboard.", new_s)
    
    new_s.uni_budget -= 60000
    new_s.uni_influence -= 6
    
    new_s.service_coordination = clamp(s.service_coordination + 10, 0, 100)
    add_to_next_transition(f"Service coordination improved to {new_s.service_coordination}% (better information sharing).", new_s)
    
    new_s.public_support = clamp(s.public_support + 6, 0, 100)
    add_to_next_transition("Public support increased (transparency and accountability).", new_s)
    
    new_s.reputation_score = clamp(s.reputation_score + 10, 0, 100)
    
    add_to_next_transition("Dashboard enables coordinated strategy across all stakeholders.", new_s)
    
    new_s.last_positive_action = True
    update_turn(new_s)
    return new_s

#------------------
# Precondition functions
#------------------

# Neighborhoods
def can_media_campaign(s):
    if s.whose_turn != NEIGHBORHOODS:
        return False
    return s.neigh_budget >= 100000 and s.public_support < 70

def can_private_security(s):
    if s.whose_turn != NEIGHBORHOODS:
        return False
    return s.neigh_budget >= 75000 and s.safety_perception < 55

def can_outreach_program(s):
    if s.whose_turn != NEIGHBORHOODS:
        return False
    return s.neigh_budget >= 60000 and s.public_support > 45

def can_community_forums(s):
    if s.whose_turn != NEIGHBORHOODS:
        return False
    return s.neigh_budget >= 15000 and s.complaint_rate > 20

# Business
def can_city_sweeps(s):
    if s.whose_turn != BUSINESS:
        return False
    return s.biz_budget >= 120000 and s.cleanliness_index < 60

def can_job_readiness(s):
    if s.whose_turn != BUSINESS:
        return False
    return s.biz_budget >= 180000 and s.turn > 3

def can_street_ambassadors(s):
    if s.whose_turn != BUSINESS:
        return False
    return s.biz_budget >= 90000 and s.biz_reputation > 40

def can_affordable_housing(s):
    if s.whose_turn != BUSINESS:
        return False
    return s.biz_budget >= 350000 and s.turn > 8

# Medical
def can_health_clinic(s):
    if s.whose_turn != MEDICAL:
        return False
    return s.med_budget >= 200000 and s.turn > 2

def can_mental_health(s):
    if s.whose_turn != MEDICAL:
        return False
    return s.med_budget >= 280000 and s.turn > 4

def can_medical_respite(s):
    if s.whose_turn != MEDICAL:
        return False
    return s.med_budget >= 160000

def can_mobile_outreach(s):
    if s.whose_turn != MEDICAL:
        return False
    return s.med_budget >= 95000 and s.turn > 2

# Shelters
def can_volunteer_drive(s):
    if s.whose_turn != SHELTERS:
        return False
    return s.shelter_budget >= 50000 and s.public_support > 45

def can_expand_shelter(s):
    if s.whose_turn != SHELTERS:
        return False
    return s.shelter_budget >= 150000

def can_housing_navigation(s):
    if s.whose_turn != SHELTERS:
        return False
    return s.shelter_budget >= 120000 and s.turn > 3

def can_establish_psh(s):
    if s.whose_turn != SHELTERS:
        return False
    return s.shelter_budget >= 400000 and s.turn > 10 and s.service_coordination > 50

def can_research_partner(s):
    if s.whose_turn != SHELTERS:
        return False
    return s.shelter_budget >= 75000 and s.turn > 5

# University
def can_student_outreach(s):
    if s.whose_turn != UNIVERSITY:
        return False
    return s.uni_budget >= 40000 and s.turn % 12 not in [0, 11, 12, 23, 24]

def can_policy_research(s):
    if s.whose_turn != UNIVERSITY:
        return False
    return s.uni_budget >= 90000 and s.turn > 4

def can_pilot_program(s):
    if s.whose_turn != UNIVERSITY:
        return False
    return s.uni_budget >= 150000 and s.research_funding >= 150000 and s.turn > 6 and not s.pilot_active

def can_academic_forums(s):
    if s.whose_turn != UNIVERSITY:
        return False
    return s.uni_budget >= 25000 and s.community_engagement < 60

def can_data_dashboard(s):
    if s.whose_turn != UNIVERSITY:
        return False
    return s.uni_budget >= 60000 and s.turn > 8

#------------------
#<OPERATORS>
NEIGHBORHOODS_OPS = [
    Operator("Launch Media Campaign",
             lambda s: can_media_campaign(s),
             lambda s: launch_media_campaign(s)),
    Operator("Fund Private Security Patrols",
             lambda s: can_private_security(s),
             lambda s: fund_private_security(s)),
    Operator("Sponsor Neighborhood Outreach",
             lambda s: can_outreach_program(s),
             lambda s: sponsor_outreach_program(s)),
    Operator("Host Community Forums",
             lambda s: can_community_forums(s),
             lambda s: host_community_forums(s))
]

BUSINESS_OPS = [
    Operator("Partner with City Sanitation (Sweeps)",
             lambda s: can_city_sweeps(s),
             lambda s: partner_city_sweeps(s)),
    Operator("Fund Job Readiness Programs",
             lambda s: can_job_readiness(s),
             lambda s: fund_job_readiness(s)),
    Operator("Deploy Street Ambassadors",
             lambda s: can_street_ambassadors(s),
             lambda s: deploy_street_ambassadors(s)),
    Operator("Support Affordable Housing Development",
             lambda s: can_affordable_housing(s),
             lambda s: support_affordable_housing(s))
]

MEDICAL_OPS = [
    Operator("Open Low-Barrier Health Clinic",
             lambda s: can_health_clinic(s),
             lambda s: open_health_clinic(s)),
    Operator("Launch Mental Health & Addiction Services",
             lambda s: can_mental_health(s),
             lambda s: launch_mental_health_services(s)),
    Operator("Establish Medical Respite Care",
             lambda s: can_medical_respite(s),
             lambda s: establish_medical_respite(s)),
    Operator("Mobile Outreach & Street Medicine",
             lambda s: can_mobile_outreach(s),
             lambda s: mobile_outreach_medicine(s))
]

SHELTERS_OPS = [
    Operator("Launch Volunteer Recruitment Drive",
             lambda s: can_volunteer_drive(s),
             lambda s: volunteer_recruitment_drive(s)),
    Operator("Expand Emergency Shelter Capacity",
             lambda s: can_expand_shelter(s),
             lambda s: expand_shelter_capacity(s)),
    Operator("Implement Housing Navigation Program",
             lambda s: can_housing_navigation(s),
             lambda s: housing_navigation_program(s)),
    Operator("Establish Permanent Supportive Housing (PSH)",
             lambda s: can_establish_psh(s),
             lambda s: establish_psh(s)),
    Operator("Partner with University for Research",
             lambda s: can_research_partner(s),
             lambda s: partner_university_research(s))
]

UNIVERSITY_OPS = [
    Operator("Launch Student Outreach & Service Learning",
             lambda s: can_student_outreach(s),
             lambda s: student_outreach_program(s)),
    Operator("Conduct Policy Research & Evaluation",
             lambda s: can_policy_research(s),
             lambda s: conduct_policy_research(s)),
    Operator("Pilot Innovative Intervention",
             lambda s: can_pilot_program(s),
             lambda s: pilot_innovation_program(s)),
    Operator("Host Community-Academic Forums",
             lambda s: can_academic_forums(s),
             lambda s: community_academic_forums(s)),
    Operator("Develop Homelessness Data Dashboard",
             lambda s: can_data_dashboard(s),
             lambda s: develop_data_dashboard(s))
]

OPERATORS = NEIGHBORHOODS_OPS + BUSINESS_OPS + MEDICAL_OPS + SHELTERS_OPS + UNIVERSITY_OPS

#</OPERATORS>

#</COMMON_CODE>

#<INITIAL_STATE>
def create_initial_state():
    return State()
#</INITIAL_STATE>

#<ROLES>
ROLES = [
    {'name': 'Neighborhoods Coalition', 'min': 1, 'max': 1},
    {'name': 'Business District Association', 'min': 1, 'max': 1},
    {'name': 'Medical Quarter Consortium', 'min': 1, 'max': 1},
    {'name': 'Shelters & Services Network', 'min': 1, 'max': 1},
    {'name': 'University Consortium', 'min': 1, 'max': 1},
    {'name': 'Observer', 'min': 0, 'max': 25}
]
#</ROLES>

#<STATE_VIS>
BRIFL_SVG = False
render_state = None
DEBUG_VIS = True

def use_BRIFL_SVG():
    """Initialize SVG rendering (not implemented for this game)"""
    global BRIFL_SVG
    BRIFL_SVG = False
    return False
#</STATE_VIS>
