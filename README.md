# HuSHPUpy

Dean Meyer and Preston Pangle

The University of Alabama in Huntsville (UAH)

2020

![example](example.png)

## What is it?

The Huntsville SHARPpy Plotting Utility (HuSHPUpy) converts raw radiosonde data into several formats and generates [SHARPpy](https://sharppy.github.io/SHARPpy/)-based Skew-T Log-P plots. It leverages several Python libraries (NumPy, Pandas, Matplotlib, SHARPpy) to convert raw iMet or Windsond files into formats compatible with [RAOB](https://www.raob.com/), SHARPpy, and a general research format. Windsond data is processed with Pandas for quality-control and ease of viewing. HuSHPUpy also outputs custom SHARPpy plots serving as quick-looks for your data.

---

## Running the program

If you're just here to run HuSHPUpy, look no further. Follow these instructions to deploy HuSHPUpy to your system:

1. Navigate to **Releases** on this GitHub repo.
1. **Download** the latest .zip package.
1. **Unzip** the downloaded package.
1. Locate hushpupy.exe inside the package folder.
1. This guide recommends creating a shortcut for the hushpupy.exe.
1. **Execute** hushpupy.exe to run HuSHPUpy.

*Note:* HuSHPUpy will dump converted sounding files and images in *C:/Converted_Soundings*

---

## Development

This section provides instructions to support future development of HuSHPUpy.

### Package dependencies

HuSHPUpy requires these packages and their dependencies to run:

* *Matplotlib <= 3.1.3*
* SHARPpy == latest
* Pandas == latest
* Pyinstaller == latest

### Building the Anaconda environment

Original development of HuSHPUpy lived on Anaconda. It's much easier to create the correct environment for HuSHPUpy on Anaconda with this command:

`conda env create -f hushpupy-env.yml`

This environment includes PyInstaller, allowing future developers to release .exe applications.

### Building the app

HuSHPUpy may run from the command line, but it runs best as a .exe application. When future developers update the HuSHPUpy scripts, they will need to rebuild the .exe with PyInstaller. Follow these steps to rebuild HuSHPUpy:

1. Through Anaconda prompt, navigate to the USP project folder.
1. Switch to the correct Conda environment by entering `conda activate hushpupy-env`
1. **Build HuSHPUpy** with the command `pyinstaller hushpupy-build.spec`
1. *Note:* As of August 2020, using PyInstaller's `--onefile` option makes USP unstable and is not recommended.
1. Some new files appear, including a *dist* directory. *dist* contains the directory *hushpupy* which holds several files including the .exe we need.
1. **Ensure that *logo.png* and *essc_logo.png* are inside *hushpupy*. HuSHPUpy will not run without these.**
1. HuSHPUpy is now built.
1. Zip up the *hushpupy* directory with your favorite tool. We prefer [7-Zip](https://www.7-zip.org/).
1. Attach this zipped file to a new GitHub release.
