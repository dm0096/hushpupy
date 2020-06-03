# The UAH Sounding Program

Dean Meyer and Preston Pangle

The University of Alabama in Huntsville (UAH)

2020

![example](example.png)

## What is it?

The UAH Sounding Program (USP) converts raw radiosonde data into several formats and generates [SHARPpy](https://sharppy.github.io/SHARPpy/)-based Skew-T Log-P plots. It leverages several Python libraries (NumPy, Pandas, Matplotlib, SHARPpy) to convert raw iMet or Windsond files into formats compatible with [RAOB](https://www.raob.com/), SHARPpy, and a general research format. Windsond data is processed with Pandas for quality-control and ease of viewing. USP also outputs custom SHARPpy plots serving as quick-looks for your data.

---

## Run the program

If you're just here to run USP, look no further. Follow these instructions to deploy USP to your system:

1. Click **Downloads** on the left hand side.
1. **Download** the repository.
1. **Unzip** the downloaded repo.
1. Copy the *dist* directory and paste it somewhere else on your system. You may discard everything else.
1. Rename *dist* to *UAH Sounding Program.*
1. **Execute** the .exe to run USP.

*Note:* USP will dump converted sounding files and images to *C:/Converted_Soundings*

---

## Development

This section provides instructions to support future development of USP.

### Build the Anaconda environment

Original development of USP lived on Anaconda. The *sharppy* library requires its own Anaconda environment. To build this environment, enter this command in Anaconda prompt:

`conda env create -f sharppy-env-pyinst.yml`

The created environment also includes PyInstaller, allowing future developers to release .exe applications.

If you want to build new .exe files and push them to this repository via Git, delete the ".exe" line in your gitignore_global.txt. Your environment should now be ready to develop USP.