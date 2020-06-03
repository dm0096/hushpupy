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

1. Click **Source** on the left side.
2. Click the README.md link from the list of files.
3. Click the **Edit** button.
4. Delete the following text: 
5. After making your change, click **Commit** and then **Commit** again in the dialog. The commit page will open and you'll see the change you just made.
6. Go back to the **Source** page.

---

## Development

This section provides instructions to support future development of USP.

### Build the Anaconda environment

Original development of USP lived on Anaconda. The *sharppy* library requires its own Anaconda environment. To build this environment, enter this command in Anaconda prompt:

`conda env create -f sharppy-env-pyinst.yml`

The created environment also includes PyInstaller, allowing future developers to release .exe applications.

If you want to build new .exe files and push them to this repository via Git, delete the ".exe" line in your gitignore_global.txt. Your environment should now be ready to develop USP.