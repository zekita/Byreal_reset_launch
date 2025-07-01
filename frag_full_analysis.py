import matplotlib.pyplot as plt
import numpy as np
from colorama import init, Fore, Style
init(autoreset=True)

# Fixed tier data (price and supply)
tiers = [
    {"price": 0.000152709, "supply": 1_600_000},
    {"price": 0.000213793, "supply": 1_600_000},
    {"price": 0.000274876, "supply": 1_600_000},
    {"price": 0.00033596,  "supply": 1_600_000},
    {"price": 0.000397044, "supply": 1_600_000},
]

# Ask for raised values for each tier
print("Enter the amount of bbSOL raised in each tier:")
for i, tier in enumerate(tiers):
    while True:
        try:
            value = int(input(f"Tier {i+1} - Price: {tier['price']:.8f} bbSOL/token: "))
            if value < 0:
                raise ValueError
            tier["raised"] = value
            break
        except Exception:
            print("Please enter a positive integer value.")

# Ask for bbSOL price in USD and estimated $FRAG price
while True:
    try:
        bbsol_usd = float(input("\nEnter the value of bbSOL in USD: "))
        frag_est_price = float(input("Enter the estimated market price of $FRAG in USD: "))
        break
    except Exception:
        print("Invalid input! Use only numbers.")

# --- Detailed simulation (like calculadora_frag.py) ---
print(f"\nSimulation: Deposit of 10 bbSOL in each tier\nEstimated sale price: ${frag_est_price:.4f} USD\n")
header = (
    f"{'Tier':>12} | {'Overfund (%)':>12} | {'% Allocated':>11} | {'bbSOL Used':>11} | {'FRAG Tokens':>12} | {'USD Spent':>11} | {'USD Received':>13} | {'Profit USD':>11} | {'Profit/Loss (%)':>15}"
)
print(header)
print("-" * len(header))

max_profit_pct = None
results_10 = []
for tier in tiers:
    capacity_bbsol = tier["supply"] * tier["price"]
    overfund = tier["raised"] / capacity_bbsol * 100
    pct_allocated = min(1.0, capacity_bbsol / (tier["raised"] + 10.0))
    bbsol_used = 10.0 * pct_allocated
    tokens_received = bbsol_used / tier["price"] if tier["price"] > 0 else 0
    usd_received = tokens_received * frag_est_price
    usd_spent = bbsol_used * bbsol_usd
    profit_usd = usd_received - usd_spent
    profit_pct = ((usd_received / usd_spent) - 1) * 100 if usd_spent > 0 else 0
    results_10.append({
        'tier': tier['price'],
        'overfund': overfund,
        'pct_allocated': pct_allocated * 100,
        'bbsol_used': bbsol_used,
        'tokens': tokens_received,
        'usd_spent': usd_spent,
        'usd_received': usd_received,
        'profit_usd': profit_usd,
        'profit_pct': profit_pct,
        'raised': tier['raised'],
        'capacity_bbsol': capacity_bbsol
    })
if results_10:
    max_profit_pct = max(r['profit_pct'] for r in results_10)

for r in results_10:
    if r['profit_pct'] == max_profit_pct:
        color = Fore.GREEN + Style.BRIGHT
    elif r['profit_pct'] > 0:
        color = Fore.YELLOW
    else:
        color = Fore.RED
    print(color + f"{r['tier']:>12.8f} | {r['overfund']:>11.2f}% | {r['pct_allocated']:>10.2f}% | {r['bbsol_used']:>10.4f} | {r['tokens']:>12.2f} | ${r['usd_spent']:>10.2f} | ${r['usd_received']:>12.2f} | ${r['profit_usd']:>10.2f} | {r['profit_pct']:>+14.2f}%")

print("\nLegend:")
print(Fore.GREEN + Style.BRIGHT + "Green: Tier with highest profit percentage")
print(Fore.YELLOW + "Yellow: Tier with real positive profit")
print(Fore.RED + "Red: Tier with real loss")
print(Style.RESET_ALL)

# --- Optimal allocation algorithm for 10 bbSOL ---
bbsol_total = 10.0
allocation = [0.0 for _ in tiers]
raised_now = [r['raised'] for r in results_10]
capacity = [r['bbsol_used'] for r in results_10]

for _ in range(int(bbsol_total)):
    best_idx = -1
    best_profit_abs = -float('inf')
    for i, r in enumerate(results_10):
        new_raised = raised_now[i] + 1.0
        real_capacity = r['capacity_bbsol']
        pct_allocated = min(1.0, real_capacity / new_raised) if new_raised > 0 else 0
        bbsol_used = 1.0 * pct_allocated
        tokens_received = bbsol_used / tiers[i]['price'] if tiers[i]['price'] > 0 else 0
        usd_received = tokens_received * frag_est_price
        usd_spent = bbsol_used * bbsol_usd
        profit_abs = usd_received - usd_spent
        if profit_abs > best_profit_abs:
            best_profit_abs = profit_abs
            best_idx = i
    allocation[best_idx] += 1.0
    raised_now[best_idx] += 1.0

total_return = 0
bbsol_used_total = 0
usd_spent_total = 0
for i, r in enumerate(results_10):
    new_raised = r['raised'] + allocation[i]
    real_capacity = r['capacity_bbsol']
    pct_allocated = min(1.0, real_capacity / new_raised) if new_raised > 0 else 0
    bbsol_used = allocation[i] * pct_allocated
    tokens_received = bbsol_used / r['tier'] if r['tier'] > 0 else 0
    usd_received = tokens_received * frag_est_price
    total_return += usd_received
    bbsol_used_total += bbsol_used
    usd_spent_total += bbsol_used * bbsol_usd
profit_total_usd = total_return - usd_spent_total

print(Fore.CYAN + f"\nOptimal allocation suggestion for 10 bbSOL (maximizing absolute profit in USD):")
for i, r in enumerate(results_10):
    print(f"  Tier {r['tier']:.8f} bbSOL: {allocation[i]:.2f} bbSOL")
print(f"\nEstimated total return: ${total_return:.2f} USD for {bbsol_used_total:.2f} bbSOL effectively used.")
print(f"Total cost: ${usd_spent_total:.2f} USD")
print(f"Estimated total profit: ${profit_total_usd:.2f} USD")
if bbsol_used_total > 0:
    print(f"Average return per bbSOL used: ${total_return / bbsol_used_total:.2f} USD")
print(f"Average return per bbSOL deposited: ${total_return / bbsol_total:.2f} USD")
print(Style.RESET_ALL)

print("\nTIP: Now the algorithm allocates each bbSOL where the marginal absolute profit is highest, maximizing your final USD profit!")

# --- GENERATE THE OPTIMAL TIERS GRAPH (RELATIVE PROFIT) ---
print("\nGenerating optimal tiers graph (relative profit)...")

precos_teste = np.linspace(0.15, 2.3, 1000)
lucros_por_tier = {i: [] for i in range(len(tiers))}
for preco_venda in precos_teste:
    for i, tier in enumerate(tiers):
        capacity_bbsol = tier["supply"] * tier["price"]
        pct_allocated = min(1.0, capacity_bbsol / (tier["raised"] + 10.0))
        bbsol_used = 10.0 * pct_allocated
        tokens_received = bbsol_used / tier["price"] if tier["price"] > 0 else 0
        usd_received = tokens_received * preco_venda
        usd_spent = bbsol_used * bbsol_usd
        profit_usd = usd_received - usd_spent
        lucros_por_tier[i].append(profit_usd)

# Calculate relative profit (spread the lines)
lucro_min = np.min([lucros_por_tier[i] for i in range(len(tiers))], axis=0)
lucros_relativos = []
for i in range(len(tiers)):
    rel = np.array(lucros_por_tier[i]) - lucro_min
    lucros_relativos.append(rel)

melhor_tier_por_preco = []
for j in range(len(precos_teste)):
    best_idx = 0
    best_profit = lucros_por_tier[0][j]
    for i in range(1, len(tiers)):
        if lucros_por_tier[i][j] > best_profit:
            best_profit = lucros_por_tier[i][j]
            best_idx = i
    melhor_tier_por_preco.append(best_idx)
thresholds = []
tier_atual = melhor_tier_por_preco[0]
for i, tier in enumerate(melhor_tier_por_preco[1:], 1):
    if tier != tier_atual:
        thresholds.append((precos_teste[i], tier_atual, tier))
        tier_atual = tier
nomes_tiers = []
for i in range(len(tiers)):
    overfund = tiers[i]["raised"] / (tiers[i]["supply"] * tiers[i]["price"]) * 100
    nome = f'Tier ${tiers[i]["price"]:.6f}\n({int(overfund)}%)\noverfund'
    nomes_tiers.append(nome)
fig, ax = plt.subplots(figsize=(14, 8))
cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
for i in range(len(tiers)):
    ax.plot(precos_teste, lucros_relativos[i], label=nomes_tiers[i], color=cores[i], linewidth=2.5)
last_x = precos_teste[0]
last_tier = melhor_tier_por_preco[0]
for i, (preco, tier_anterior, tier_novo) in enumerate(thresholds):
    ax.axvspan(last_x, preco, color=cores[last_tier], alpha=0.08)
    x_centro = (last_x + preco) / 2
    y_centro = ax.get_ylim()[1] * 0.85
    ax.text(x_centro, y_centro, nomes_tiers[last_tier], color=cores[last_tier],
             fontsize=12, ha='center', va='center', alpha=0.7, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.3'))
    last_x = preco
    last_tier = tier_novo
ax.axvspan(last_x, precos_teste[-1], color=cores[last_tier], alpha=0.08)
x_centro = (last_x + precos_teste[-1]) / 2
y_centro = ax.get_ylim()[1] * 0.85
ax.text(x_centro, y_centro, nomes_tiers[last_tier], color=cores[last_tier],
         fontsize=12, ha='center', va='center', alpha=0.7, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.3'))
for preco, tier_anterior, tier_novo in thresholds:
    ax.axvline(x=preco, color='red', linestyle='--', alpha=0.8, linewidth=1.5)
    ax.text(preco, ax.get_ylim()[1]*0.95, f'${preco:.2f}', rotation=90, ha='right', va='top', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
ax.set_xlabel('Estimated Market Price (USD)', fontsize=14, fontweight='bold')
ax.set_ylabel('Relative Profit (USD)', fontsize=14, fontweight='bold')
ax.set_title(f'Relative Profit per Tier vs Estimated Market Price\n(10 bbSOL, bbSOL = ${bbsol_usd})', fontsize=16, fontweight='bold')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xlim(0.15, 2.3)
plt.tight_layout()
plt.show() 