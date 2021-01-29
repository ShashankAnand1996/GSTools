"""
Automatically fitting
---------------------

Here we generate synthetic lognormal data, that should be interpolated
Here we transform a field to a log-normal distribution:
"""
import numpy as np
import gstools as gs
import matplotlib.pyplot as plt

# structured field with a size of 60x60
x = y = range(60)
pos = gs.tools.geometric.gen_mesh([x, y])
model = gs.Gaussian(dim=2, var=1, len_scale=10)
srf = gs.SRF(model, seed=20170519, normalizer=gs.normalizer.LogNormal())
srf(pos)

###############################################################################
# Now we want to interpolate the given field to finer resolution (down-scaling)
# and we want to normalize the given data with the BoxCox transformation.
#
# First, we convert the given condtions to be unstructured
# and set the output resolution.
#
# To make the data more scarce, we will sample 60 points.

ids = np.arange(srf.field.size)
sampled = np.random.RandomState(20210201).choice(ids, size=60, replace=False)

# sample conditioning points from generated field
cond_pos = pos[:, sampled]
cond_val = srf.field[sampled]

###############################################################################
# Now we set up the kriging routine. We use a :any:`Stable` model, that should
# be fitted to the given data (by setting ``fit_variogram=True``) and we
# use the :any:`BoxCox` normalizer in order to gain normality.
#
# The BoxCox normalizer will be fitted automatically to the data,
# by setting ``fit_normalizer=True``.

krige = gs.krige.Ordinary(
    model=gs.Stable(dim=2),
    cond_pos=cond_pos,
    cond_val=cond_val,
    normalizer=gs.normalizer.BoxCox(),
    fit_normalizer=True,
    fit_variogram=True,
)

###############################################################################
# First, let's have a look at the fitting results:

print(krige.model)
print(krige.normalizer)

###############################################################################
# As we see, it went quite well. Variance is a bit underestimated, but
# length scale and nugget are good. The shape parameter of the stable model
# is correctly estimated to be close to `2`,
# so we result in a gaussian like model.
#
# The BoxCox parameter `lmbda` was estimated to be almost 0, which means,
# the log-normal distribution was correctly fitted.
#
# Now let's run the kriging interpolation and let's have a look at the
# resulting field. We will also generate the original field for comparison.

# interpolate
krige(pos)

# plot
fig, ax = plt.subplots(1, 3, figsize=[8, 3])
ax[0].imshow(srf.field.reshape(60, 60).T, origin="lower")
ax[1].scatter(*cond_pos, c=cond_val)
ax[2].imshow(krige.field.reshape(60, 60).T, origin="lower")
# titles
ax[0].set_title("original field")
ax[1].set_title("sampled field")
ax[2].set_title("interpolated field")
# set aspect ratio to equal in all plots
[ax[i].set_aspect("equal") for i in range(3)]
