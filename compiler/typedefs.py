from type import Type

# ================
# Valid sire types
# ================
#
# Global declarations:
#  - T_VAL_SINGLE
#
# Local declarations:
#  - T_VAR_SINGLE
#  - T_VAR_ARRAY
#  - T_REF_ARRAY
#  - T_CHAN_SINGLE
#  - T_CHAN_ARRAY
#  - T_CHANEND_SINGLE
#
# Formal parameters:
#  - T_VAL_SINGLE
#  - T_REF_SINGLE
#  - T_REF_ARRAY
#  - T_CHANEND_SINGLE
#
# (extra) Elements:
#  - T_VAR_SUB
#  - T_CHAN_SUB
#  - T_CORE_SUB 

# Single value
T_VAL_SINGLE     = Type('val', 'single')

# Single variables
T_VAR_SINGLE     = Type('var', 'single')
T_VAL_SUB        = Type('val', 'sub')
T_VAR_SUB        = Type('var', 'sub')
T_REF_SINGLE     = Type('ref', 'single')
T_REF_SUB        = Type('ref', 'sub')

# Single channels and channel ends
T_CHAN_SINGLE    = Type('chan', 'single')
T_CHAN_SUB       = Type('chan', 'sub')
T_CHANEND_SINGLE = Type('chanend', 'single')
T_CHANEND_SUB    = Type('chanend', 'sub')

# Variable arrays
T_VAR_ARRAY      = Type('var', 'array') 
T_REF_ARRAY      = Type('ref', 'array')

# Channel arrays
T_CHAN_ARRAY     = Type('chan', 'array')

# Procedures
T_PROC           = Type('proc', 'procedure')
T_FUNC           = Type('func', 'procedure')

# Tag
T_TAG            = Type('tag')

