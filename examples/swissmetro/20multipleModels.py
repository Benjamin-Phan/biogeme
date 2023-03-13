"""File 20multipleModels.py

:author: Michel Bierlaire, EPFL
:date: Mon Mar  6 15:15:56 2023

 Example of the estimation of several versions of the model
 Three alternatives: Train, Car and Swissmetro
 SP data
"""

import biogeme.biogeme as bio
from biogeme import models
from biogeme.expressions import Beta, log
from biogeme.results import compileEstimationResults
from biogeme.multiple_expressions import NamedExpression, Catalog
from swissmetro import (
    database,
    CHOICE,
    SM_AV,
    CAR_AV_SP,
    TRAIN_AV_SP,
    TRAIN_TT_SCALED,
    TRAIN_COST_SCALED,
    SM_TT_SCALED,
    SM_COST_SCALED,
    CAR_TT_SCALED,
    CAR_CO_SCALED,
    MALE,
)

# Parameters to be estimated
ASC_CAR = Beta('ASC_CAR', 0, None, None, 0)
ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 0)
ASC_CAR_MALE = Beta('ASC_CAR_MALE', 0, None, None, 0)
ASC_CAR_FEMALE = Beta('ASC_CAR_FEMALE', 0, None, None, 0)
ASC_TRAIN_MALE = Beta('ASC_TRAIN_MALE', 0, None, None, 0)
ASC_TRAIN_FEMALE = Beta('ASC_TRAIN_FEMALE', 0, None, None, 0)
B_TIME = Beta('B_TIME', 0, None, None, 0)
B_COST = Beta('B_COST', 0, None, None, 0)

SEGMENTED_ASC_CAR = MALE * ASC_CAR_MALE + (1 - MALE) * ASC_CAR_FEMALE
SEGMENTED_ASC_TRAIN = MALE * ASC_TRAIN_MALE + (1 - MALE) * ASC_TRAIN_FEMALE

homog_asc_car = NamedExpression(name='homog_asc_car', expression=ASC_CAR)
homog_asc_train = NamedExpression(name='homog_asc_train', expression=ASC_TRAIN)

seg_asc_car = NamedExpression(name='seg_asc_car', expression = SEGMENTED_ASC_CAR)
seg_asc_train = NamedExpression(name='seg_asc_train', expression = SEGMENTED_ASC_TRAIN)

ASC_CAR_catalog = Catalog('ASC_CAR_catalog', (homog_asc_car, seg_asc_car))
ASC_TRAIN_catalog = Catalog('ASC_TRAIN_catalog', (homog_asc_train, seg_asc_train))
                          

# Definition of the utility functions with linear cost
V1 = ASC_TRAIN_catalog + B_TIME * TRAIN_TT_SCALED + B_COST * TRAIN_COST_SCALED
V2 = B_TIME * SM_TT_SCALED + B_COST * SM_COST_SCALED
V3 = ASC_CAR_catalog + B_TIME * CAR_TT_SCALED + B_COST * CAR_CO_SCALED

# Associate utility functions with the numbering of alternatives
V = {1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {1: TRAIN_AV_SP, 2: SM_AV, 3: CAR_AV_SP}

# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.loglogit(V, av, CHOICE)
linear_spec = NamedExpression(name='linear_spec', expression=logprob)


# We now consider a model with the log travel time instead of the cost
# Definition of the utility functions with log cost
log_V1 = ASC_TRAIN + B_TIME * log(TRAIN_TT_SCALED) + B_COST * TRAIN_COST_SCALED
log_V2 = B_TIME * log(SM_TT_SCALED) + B_COST * SM_COST_SCALED
log_V3 = ASC_CAR + B_TIME * log(CAR_TT_SCALED) + B_COST * CAR_CO_SCALED

# Associate utility functions with the numbering of alternatives
log_V = {1: log_V1, 2: log_V2, 3: log_V3}

log_logprob = models.loglogit(log_V, av, CHOICE)

log_spec = NamedExpression(name='log_spec', expression=log_logprob)

catalog_of_expressions = Catalog(
    'loglikelihood',
    (linear_spec, log_spec)
)

biogeme = bio.BIOGEME(database, catalog_of_expressions)
results = biogeme.estimate()

for name, r in results.items():
    print('========')
    print(name)
    print('========')
    print(r)
#summary = compileEstimationResults(results)

#print(summary)
