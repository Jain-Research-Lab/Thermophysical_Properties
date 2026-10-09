from DOA.config.lib_config import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

def plot_3d_compare(XREF, YREF, ZREF, XDAT, YDAT, ZDAT, xtext, ytext, ztext, num, mode):
    if mode >= 0:
        # fig0 = plt.figure(num)
        # ax0 = fig0.add_subplot(111, projection='3d')
        # ax0.scatter(XREF, YREF, ZREF, c='b', marker='x', s=0.1, label="REF")
        # ax0.scatter(XDAT, YDAT, ZDAT, c='g', marker='x', s=1, label="DAT")
        # ax0.set_xlabel(xtext)
        # ax0.set_ylabel(ytext)
        # ax0.set_zlabel(ztext)
        # ax0.legend()
        
        fig0 = plt.figure(num)
        ax0 = fig0.add_subplot(111, projection='3d')
        surf = ax0.plot_surface(XREF, YREF, ZREF, cmap='viridis', alpha=0.6, edgecolor='none')
        ax0.scatter(XDAT, YDAT, ZDAT, c='g', marker='x', s=10)
        ax0.set_xlabel(xtext)
        ax0.set_ylabel(ytext)
        ax0.set_zlabel(ztext)
        surf._edgecolors2d = surf._edgecolor3d
        surf._facecolors2d = surf._facecolor3d
        ax0.legend()
    
    if mode >= 1:
        fig1 = plt.figure(num+1)
        ax1 = fig1.add_subplot(111, projection='3d')
        ax1.scatter(XREF, YREF, np.abs(ZREF - ZDAT), c='b', marker='x', s=1)
        ax1.set_xlabel(xtext)
        ax1.set_ylabel(ytext)
        ax1.set_zlabel("Absolute Error")
    
    if mode >= 2:
        fig2 = plt.figure(num+2)
        ax2 = fig2.add_subplot(111, projection='3d')
        ax2.scatter(XREF, YREF, np.clip(np.abs(ZREF - ZDAT) / np.abs(ZREF), 0, 1), c='b', marker='x', s=1)
        ax2.set_xlabel(xtext)
        ax2.set_ylabel(ytext)
        ax2.set_zlabel("Relative Error")


def plot_accuracy(hr, Pr, Tr, Tr_REF, Dr, Dr_REF, Er, Er_REF, xtext, ytext):
    # fig1 = plt.figure()
    # ax1 = fig1.add_subplot(111, projection='3d')
    # ax1.scatter(hr, Pr, Tr - Tr_REF, c='b', marker='x', s=1)
    # ax1.set_xlabel(xtext)
    # ax1.set_ylabel(ytext)
    # ax1.set_zlabel("Absolute Error")

    Tr = np.flipud(Tr)
    Dr = np.flipud(Dr)
    Er = np.flipud(Er)

    Tr_REF = np.flipud(Tr_REF)
    Dr_REF = np.flipud(Dr_REF)
    Er_REF = np.flipud(Er_REF)

    eps_rel = 1e-8

    plt.figure()
    eTr = np.clip(np.abs(Tr - Tr_REF), eps_rel, 100)
    plt.imshow(eTr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eTr), vmax=np.nanmax(eTr)),)
    plt.colorbar()

    plt.figure()
    eDr = np.clip(np.abs(Dr - Dr_REF), eps_rel, 100)
    plt.imshow(eDr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eDr), vmax=np.nanmax(eDr)),)
    plt.colorbar()

    plt.figure()
    eEr = np.clip(np.abs(Er*1000 - Er_REF), eps_rel, 100)
    plt.imshow(eEr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eEr), vmax=np.nanmax(eEr)),)
    plt.colorbar()

    plt.figure()
    eTr = np.clip((np.abs(Tr - Tr_REF) / Tr_REF), eps_rel, 100)
    plt.imshow(eTr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eTr), vmax=np.nanmax(eTr)),)
    plt.colorbar()

    plt.figure()
    eDr = np.clip((np.abs(Dr - Dr_REF) / Dr_REF), eps_rel, 100)
    plt.imshow(eDr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eDr), vmax=np.nanmax(eDr)),)
    plt.colorbar()

    plt.figure()
    eEr = np.clip((np.abs(Er*1000 - Er_REF) / Er_REF), eps_rel, 100)
    plt.imshow(eEr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eEr), vmax=np.nanmax(eEr)),)
    plt.colorbar()
    
    plt.figure()
    plt.imshow(np.abs(Tr - Tr_REF), cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Dr - Dr_REF), cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Er*1000 - Er_REF), cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Tr - Tr_REF) / Tr_REF, cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Dr - Dr_REF) / Dr_REF, cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Er*1000 - Er_REF) / np.abs(Er_REF), cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(Dr, cmap="viridis")
    plt.colorbar()

    plt.show()


    return 1

def plot_accuracy2(Tr, Dr, hr, hr_REF, Pr, Pr_REF, Er, Er_REF, xtext, ytext):
    hr = np.flipud(hr)*1000 + 100_000
    Pr = np.flipud(Pr)*1000
    Er = np.flipud(Er)*1000 + 100_000

    hr_REF = np.flipud(hr_REF) + 100_000
    Pr_REF = np.flipud(Pr_REF)
    Er_REF = np.flipud(Er_REF) + 100_000

    eps_rel = 1e-4

    plt.figure()
    eTr = np.clip(np.abs(hr - hr_REF), eps_rel, 10000)
    plt.imshow(eTr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eTr), vmax=np.nanmax(eTr)),)
    plt.colorbar()

    plt.figure()
    eDr = np.clip(np.abs(Pr - Pr_REF), eps_rel, 10000)
    plt.imshow(eDr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eDr), vmax=np.nanmax(eDr)),)
    plt.colorbar()

    plt.figure()
    eEr = np.clip(np.abs(Er - Er_REF), eps_rel, 10000)
    plt.imshow(eEr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eEr), vmax=np.nanmax(eEr)),)
    plt.colorbar()

    plt.figure()
    eTr = np.clip((np.abs(hr - hr_REF) / np.abs(hr_REF)), eps_rel, 10000)
    plt.imshow(eTr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eTr), vmax=np.nanmax(eTr)),)
    plt.colorbar()

    plt.figure()
    eDr = np.clip((np.abs(Pr - Pr_REF) / Pr_REF), eps_rel, 10000)
    plt.imshow(eDr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eDr), vmax=np.nanmax(eDr)),)
    plt.colorbar()

    plt.figure()
    eEr = np.clip((np.abs(Er - Er_REF) / np.abs(Er_REF)), eps_rel, 10000)
    plt.imshow(eEr, cmap="viridis", norm=LogNorm(vmin=np.nanmin(eEr), vmax=np.nanmax(eEr)),)
    plt.colorbar()
    
    plt.figure()
    plt.imshow(np.abs(hr - hr_REF), cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Pr - Pr_REF), cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Er - Er_REF), cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(hr - hr_REF) / np.abs(hr_REF), cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Pr - Pr_REF) / Pr_REF, cmap="viridis")
    plt.colorbar()

    plt.figure()
    plt.imshow(np.abs(Er - Er_REF) / np.abs(Er_REF), cmap="viridis")
    plt.colorbar()

    # plt.figure()
    # plt.imshow(Dr, cmap="viridis")
    # plt.colorbar()

    plt.show()


    return 1