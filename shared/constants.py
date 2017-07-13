# all shared constants or variables will go here

feature_type = [
                ('','Select'),
                ('top','top'),
                ('count','count'),
                ('distinct','distinct'),
                ('request','request'),
                #('internal','internal'),
                ('config','config'),
                ('hashkey','hashkey'),
                ('key','key'),
                ('collection','collection')
                ]



type_on_fields = [
                    ('','Select'),
                    ('apidata.__uzma','apidata.__uzma'),
                    ('apidata.__uzmc','apidata.__uzmc'),
                    ('apidata._zpsbd3','apidata._zpsbd3'),
                    ('apidata._zpsbd4','apidata._zpsbd4'),
                    ('apidata._zpsbd5','apidata._zpsbd5'),
                    ('apidata._zpsbd6','apidata._zpsbd6'),
                    ('apidata._zpsbd7','apidata._zpsbd7'),
                    ('apidata._zpsbd9','apidata._zpsbd9'),
                    ('d_uzmc','d_uzmc')
                ]

FEATURE_WITH_FIELDS = ['top','distinct']

# redis keys 

Z_G_RULES = 'Z:G_RULES'
Z_SID_RULE_PREFIX = 'Z:RULES:'
K_G_RULE_TABLE_V = 'K:RuleTableVersion'
K_SID_TABLE_V_PREFIX = 'H:sid:'
K_SID_TABLE_V_FIELD = 'ruleTableVersion'
K_HASH_FEATURES = 'H:G_RULE_FEATURES'
K_VTABLE_FEATURES = 'K:FeatureTableVersion'
K_HASH_CONSTANT = 'H:G_RULES_CONSTANT'
K_VTABLE_CONSTANT = 'K:ConstantTableVersion'
K_HASH_PERC = 'H:G:RULES_PERC'
K_VTABLE_PERC = 'K:PercTableVersion'

#mysql connection settings

DATA_BASE_MYSQL = { "host":"104.154.25.198",
                   "user" : "ssuser",
                   "password":"jnvskjvnksdvnslczfdszv",
                   "db_name":"prod-mysql-db"
                   };
