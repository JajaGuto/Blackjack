from scipy.signal import lfilter
import scipy.stats as st
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

balances = np.load('balances.npy', mmap_mode='r')
balances = balances.T

color = {'flat_bet': 'dodgerblue', 'martingale': 'springgreen', 'paroli': 'deeppink', 'fibbonacci': 'orange', 'dalambert': 'olive'}

k_color = list(color.keys())

print(balances.shape)
players_number = 5
turn_number = 101
games_number = 15000

balances_mean = []
means = []

upper = [0 for _ in range(players_number)]
big_loss_count = [0 for _ in range(players_number)]
negative_count = [0 for _ in range(players_number)]
positive_count = [0 for _ in range(players_number)]
big_win_count  = [0 for _ in range(players_number)]

success = [[False for _ in range(games_number)] for _ in range(players_number)]

for player in range(players_number):
    means = []
    for game in range(games_number):
        this = balances[player][game*101+100]
        if this >= 1000:
            success[player][game] = True
            if this >= 1500:
                big_win_count[player] += 1
            else:
                positive_count[player] += 1
        else:
            if this <= 100:
                big_loss_count[player] += 1
            else:
                negative_count[player] += 1
        if this > upper[player]:
            upper[player] = this

for i in range(players_number):
    print(" {}: higher {} / counter on levels of success: {} {} {} {}.".format(k_color[i].replace("_", " "),upper[i],big_loss_count[i], negative_count[i], positive_count[i],big_win_count[i]))


print(positive_count)


# counting wins, ties losses
win_counter = [0 for _ in range(players_number)]
tie_counter = [0 for _ in range(players_number)]
lose_counter = [0 for _ in range(players_number)]
wins = np.load('wins.npy', mmap_mode='r')
wins = wins.T
losses = np.load('losses.npy', mmap_mode='r')
losses = losses.T
bets = np.load('bets.npy', mmap_mode='r')
bets = bets.T

turn_number = 100

for player in range(players_number):
    means = []
    for turn in range(turn_number):
        for game in range(games_number):
            lose_counter[player] += losses[player][game*turn_number+turn]
            win_counter[player] += wins[player][game*turn_number+turn]
            if wins[player][game*turn_number+turn] == 0 and losses[player][game*turn_number+turn] == 0 and bets[player][game*turn_number+turn] > 0:
                tie_counter[player] += 1

    
for i in range(players_number):
    print(" {}: higher {} / total wins ties and lossess: {} {} {}.".format(k_color[i].replace("_", " "),upper[i],win_counter[i],tie_counter[i], lose_counter[i]))



# Plot dos jogos em que os jogadores sairam lucrando
confidence_interval = []
for player in range(players_number):
    confidence_low = []
    confidence_high = []
    means = []
    for turn in range(turn_number):
        aux = []
        sum_turn = 0
        for game in range(games_number):
            if success[player][game]:
                sum_turn += balances[player][game*turn_number+turn]
                aux.append(balances[player][game*turn_number+turn])
        means.append(sum_turn/positive_count[player])
        confidence_lower, confidence_higher = st.t.interval(alpha=0.95, df=len(aux)-1,
                                                                              loc=np.mean(aux),
                                                                              scale=st.sem(aux))
        confidence_low.append(confidence_lower)
        confidence_high.append(confidence_higher)
    confidence_interval.append([confidence_low, confidence_high])
    balances_mean.append(means.copy())
print(balances_mean)

matplotlib.rcParams.update({'font.size': 18})
fig, ax = plt.subplots()
fig.set_size_inches(11, 8)

# means = lfilter(b, a, cash_log_mean)
# means2, stds = mfilter(rewards, n)
for i, balance_mean in enumerate(balances_mean):
    #balance_mean[0:n - 1] = 1000
    confidence_low, confidence_high = confidence_interval[i]
    ax.plot(range(101), balance_mean, linestyle='-', linewidth=2, label=k_color[i].replace("_", " "), c=color[k_color[i]])
    ax.fill_between(range(101), confidence_low, confidence_high, alpha=0.1, facecolor=color[k_color[i]])

ax.legend(loc="upper left", mode="expand", ncol=3, prop={'size': 20})
ax.set_xlabel('Game Turn', fontsize=20)
ax.set_ylabel('Balance', fontsize=20)
#ax.set_xlim([0, x_lim[sel[-1]]])
#ax.set_ylim([-45, 201])
ax.grid()
fig.set_dpi(100)
plt.savefig("balance_pos.pdf", format="pdf", bbox_inches="tight")
plt.show()

balances_mean = []


# Plot dos jogos em que os jogadores sairam perdendo
confidence_interval = []
for player in range(players_number):
    confidence_low = []
    confidence_high = []
    means = []
    for turn in range(turn_number):
        aux = []
        sum_turn = 0
        for game in range(games_number):
            if not success[player][game]:
                sum_turn += balances[player][game*turn_number+turn]
                aux.append(balances[player][game*turn_number+turn])
        means.append(sum_turn/(games_number-positive_count[player]))
        confidence_lower, confidence_higher = st.t.interval(alpha=0.95, df=len(aux)-1,
                                                                              loc=np.mean(aux),
                                                                              scale=st.sem(aux))
        confidence_low.append(confidence_lower)
        confidence_high.append(confidence_higher)
    confidence_interval.append([confidence_low, confidence_high])
    balances_mean.append(means.copy())
print(balances_mean)


matplotlib.rcParams.update({'font.size': 18})
fig, ax = plt.subplots()
fig.set_size_inches(11, 8)

# means = lfilter(b, a, cash_log_mean)
# means2, stds = mfilter(rewards, n)
for i, balance_mean in enumerate(balances_mean):
    #balance_mean[0:n - 1] = 1000
    confidence_low, confidence_high = confidence_interval[i]
    ax.plot(range(101), balance_mean, linestyle='-', linewidth=2, label=k_color[i].replace("_", " "), c=color[k_color[i]])
    ax.fill_between(range(101), confidence_low, confidence_high, alpha=0.1, facecolor=color[k_color[i]])

ax.legend(loc="lower left", mode="expand", ncol=3, prop={'size': 20})
ax.set_xlabel('Game Turn', fontsize=20)
ax.set_ylabel('Balance', fontsize=20)
#ax.set_xlim([0, x_lim[sel[-1]]])
#ax.set_ylim([-45, 201])
ax.grid()
fig.set_dpi(100)
plt.savefig("balance_neg.pdf", format="pdf", bbox_inches="tight")
plt.show()
    

stds = []
print(stds)
balances_mean = []
confidence_interval = []
for player in range(players_number):
    confidence_low = []
    confidence_high = []
    aux_std = []
    means = []
    for turn in range(turn_number):
        aux = []
        sum_turn = 0
        for game in range(games_number):
            sum_turn += balances[player][game*turn_number+turn]
            aux.append(balances[player][game*turn_number+turn])
        means.append(sum_turn/games_number)
        confidence_lower, confidence_higher = st.t.interval(alpha=0.95, df=len(aux)-1,
                                                                              loc=np.mean(aux),
                                                                              scale=st.sem(aux))
        confidence_low.append(confidence_lower)
        confidence_high.append(confidence_higher)
        aux_std.append(np.std(aux))
    stds.append(aux_std)
    confidence_interval.append([confidence_low, confidence_high])
    balances_mean.append(means.copy())

print(balances_mean)

matplotlib.rcParams.update({'font.size': 18})
fig, ax = plt.subplots()
fig.set_size_inches(11, 8)

# means = lfilter(b, a, cash_log_mean)
# means2, stds = mfilter(rewards, n)



for i, balance_mean in enumerate(balances_mean):
    #balance_mean[0:n - 1] = 1000
    confidence_low, confidence_high = confidence_interval[i]
    ax.plot(range(101), balance_mean, linestyle='-', linewidth=2, label=k_color[i].replace("_", " "), c=color[k_color[i]])
    ax.fill_between(range(101), confidence_low, confidence_high, alpha=0.1, facecolor=color[k_color[i]])
    
    print("Mean: {}\nConfidence Interval for {}: {} <= p <= {}".format(balance_mean[-1], k_color[i].replace("_", " "),
                                                                       confidence_low[-1], confidence_high[-1]))
    print("SD: {}\n".format(stds[i][-1]))
    print(" - ")

#for i, cash_mean in enumerate(balances_mean):
#    ax.plot(range(101), cash_mean, linestyle='-', linewidth=2, label="Agent {}".format(i))

ax.legend(loc="lower left", mode="expand", ncol=3, prop={'size': 20})
ax.set_xlabel('Game Turn', fontsize=20)
ax.set_ylabel('Balance', fontsize=20)
#ax.set_xlim([0, x_lim[sel[-1]]])
#ax.set_ylim([-45, 201])
ax.grid()
fig.set_dpi(100)
plt.savefig("balance.pdf", format="pdf", bbox_inches="tight")
plt.show()

players_number = 5
turn_number = 100

win_means = []
means = []
total_wins = []
total_lose = []
total_tie = []
total_no_money = []


for player in range(players_number):
    means = []
    for turn in range(turn_number):
        sum_turn = 0
        for game in range(games_number):
            sum_turn += losses[player][game*turn_number+turn]
            sum_turn += wins[player][game*turn_number+turn]
        means.append(sum_turn/games_number)
    win_means.append(means.copy())


matplotlib.rcParams.update({'font.size': 18})
fig, ax = plt.subplots()
fig.set_size_inches(11, 8)

# means = lfilter(b, a, cash_log_mean)
# means2, stds = mfilter(rewards, n)

for i, win in enumerate(win_means):
    #balance_mean[0:n - 1] = 1000
    ax.plot(range(100), win, linestyle='-', linewidth=2, label=k_color[i].replace("_", " "), c=color[k_color[i]])

#for i, cash_mean in enumerate(win_means):
#    ax.plot(range(101), cash_mean, linestyle='-', linewidth=2, label="Agent {}".format(i))

ax.legend(loc="lower left", mode="expand", ncol=3, prop={'size': 20})
ax.set_xlabel('Game Turn', fontsize=20)
ax.set_ylabel('Win mean', fontsize=20)
#ax.set_xlim([0, x_lim[sel[-1]]])
#ax.set_ylim([-45, 201])
ax.grid()
fig.set_dpi(100)
plt.savefig("wins.pdf", format="pdf", bbox_inches="tight")
plt.show()




print(bets.shape)
players_number = 5
turn_number = 100

bets_mean = []
means = []

for player in range(players_number):
    means = []
    for turn in range(turn_number):
        sum_turn = 0
        for game in range(games_number):
            sum_turn += bets[player][game*turn_number+turn]
        means.append(sum_turn/games_number)
    bets_mean.append(means.copy())

matplotlib.rcParams.update({'font.size': 18})
fig, ax = plt.subplots()
fig.set_size_inches(11, 8)

# means = lfilter(b, a, cash_log_mean)
# means2, stds = mfilter(rewards, n)

for i, bet in enumerate(bets_mean):
    #balance_mean[0:n - 1] = 1000
    ax.plot(range(100), bet, linestyle='-', linewidth=2, label=k_color[i].replace("_", " "), c=color[k_color[i]])
    
#for i, cash_mean in enumerate(bets_mean):
#    ax.plot(range(101), cash_mean, linestyle='-', linewidth=2, label="Agent {}".format(i))

ax.legend(loc="lower left", mode="expand", ncol=3, prop={'size': 20})
ax.set_xlabel('Game Turn', fontsize=20)
ax.set_ylabel('Bet', fontsize=20)
#ax.set_xlim([0, x_lim[sel[-1]]])
ax.set_ylim([-0, 45])
ax.grid()
fig.set_dpi(100)
plt.savefig("bets.pdf", format="pdf", bbox_inches="tight")
plt.show()


