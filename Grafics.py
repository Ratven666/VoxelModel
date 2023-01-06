import numpy as np
import matplotlib.pyplot as plt

data = []

with open(r"data_for_grafics/10-1.25.csv", "r") as rf:
    for line in rf:
        data.append(line.strip().split(",")[6])

data = [float(i) for i in data[1:] if i != ""]
data.sort()
data = data[:-400]
# print(len(data))

fig, ax = plt.subplots()
x = np.array(data)
mu = x.mean()
median = np.median(x)
sigma = x.std()
textstr = '\n'.join((
    r'$\mu=%.2f$' % (mu, ),
    r'$\mathrm{median}=%.2f$' % (median, ),
    r'$\sigma=%.2f$' % (sigma, )))

step = 0.1
n = int(round((max(x) - min(x)) / step))

ax.hist(x, n)
# these are matplotlib.patch.Patch properties
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

# place a text box in upper left in axes coords
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.show()
