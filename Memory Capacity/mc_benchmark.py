import numpy as np


def mc_benchmark(file_path):
    # Set up feedback strengths
    rep = np.arange(0, 51, 1)

    DIRECTORY = "/Users/paulpickering/Library/CloudStorage/OneDrive-Personal/Uni/Placement/Mackey-Glass-Circuit/Simulations/NGSpice/MGNGSpice/Memory Capacity"

    #Choose filepath
    file_path1=f"{DIRECTORY}/MC.txt"

    #Open single column data file
    raw_signal=np.genfromtxt(file_path1)

    # Create the 'shift register' of delayed inputs for training/testing
    shift_register = np.zeros((999, 10))
    for i in range(989):
        i += 9
        shift_register[i, :] = raw_signal[i-8:i+2]

    shift_register = np.fliplr(shift_register)
    
    # Wash out starting conditions
    wash, raw_signal = np.split(raw_signal, [100])
    wash, train_target, test_target = np.split(shift_register, [100, 899])

    # Define samplerate and number of virtual nodes
    Nvirt = 100
    samplerate = 1

    # Set up outputs
    MCs = []

    # Loop over feedback strengths
    #for r in rep:
        # Load data if it exists

    #fname = f"{DIRECTORY}/OutputData_MC.txt"
    AllData = np.genfromtxt(file_path)

    amr = AllData

    # Reshapes the signal into timestep-by-timestep
    reshaped_signal = np.reshape(amr, (999, samplerate*Nvirt))

    # Wash out and split into training/testing groups
    junk, train_states, test_states = np.split(reshaped_signal, [100, 899])
    # Set up matrices for training
    X = train_states
    Yt = train_target
    M1 = np.matmul(X.transpose(), Yt) 
    M2 = np.matmul(X.transpose(), X)
    gammas = np.logspace(-10, 0, num=10)
    BestMC = 0
    BestGamma = 0  
    # Hyperparameter tuning and calculating MC
    for gamma in gammas:
        weights = np.matmul(np.linalg.pinv(M2+gamma*np.identity(len(M2))), M1)
        train_prediction = np.matmul(train_states, weights)
        test_prediction = np.matmul(test_states, weights)
        train_error = abs(train_prediction - train_target)
        MC_k = np.zeros(10)
        targVar = np.var(raw_signal[600:800])
        for node in range(10):
            Mat1 = test_prediction[:, node]
            Mat2 = test_target[:, node]
            M = Mat1, Mat2
            coVarM = np.cov(M)
            coVar = coVarM[0,1]
            outVar = np.var(Mat1)
            totVar = outVar*targVar
            if coVar**2/totVar > 0.1:
                MC_k[node] = coVar**2/totVar
        MC = sum(MC_k)
        if BestMC < MC:
            BestMC = MC

    print(BestMC)
    weights = np.matmul(np.linalg.pinv(M2+BestGamma*np.identity(len(M2))), M1)
    test_prediction = np.matmul(test_states, weights)
    return BestMC