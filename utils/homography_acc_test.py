import matplotlib.pyplot as plt
import numpy as np
import textwrap

# Example data
actual = [(6.2, 11.5), (2, 6.5), (11, 6.5), (3.5, 10.5)]
calculated = [(6.55, 11.88), (1.66, 6.62), (10.68, 6.53), (3.81, 10.91)]

# Compute errors
actual_np = np.array(actual)
calculated_np = np.array(calculated)
errors = np.linalg.norm(actual_np - calculated_np, axis=1)
mean_error = np.mean(errors)
rmse = np.sqrt(np.mean(errors**2))
max_error = np.max(errors)

# Format text
t = f"Errors per point: {errors}\n" \
    f"Mean Error: {mean_error:.4f} m\n" \
    f"RMSE: {rmse:.4f} m\n" \
    f"Max Error: {max_error:.4f} m"
tt = textwrap.fill(t, width=70)

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
for (xa, ya), (xc, yc) in zip(actual, calculated):
    ax.plot([xa, xc], [ya, yc], 'r--')
    ax.plot(xa, ya, 'go')
    ax.plot(xc, yc, 'bo')

ax.legend(['Error line', 'Actual', 'Calculated'])
ax.set_title("Homography Error Visualization")
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.grid(True)
ax.set_aspect('equal')

# Adjust limits to create more space below the plot
xlim = ax.get_xlim()
ylim = ax.get_ylim()
y_margin = (ylim[1] - ylim[0]) * 0.15  # 15% margin
ax.set_ylim(ylim[0] - y_margin, ylim[1])  # extend y-axis downward

# Add text below plot
ax.text(
    x=(xlim[0] + xlim[1]) / 2,
    y=ylim[0] - y_margin * 0.6, #13.3,  # Position text below the plot
    s=tt,
    ha='center',
    va='top',
    fontsize=9,
    bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5')
)

plt.show()
