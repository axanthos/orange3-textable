.. meta::
   :description: Orange Textable documentation, MacOS X installation
   :keywords: Orange, Textable, documentation, MacOS X, installation

MacOS X installation
====================

1. On the `Orange 2.7 download page <http://orange.biolab.si/orange2/>`_, 
   download the software installer by following the *Orange 2.7 bundle for OSX* 
   link.

2. In the window that opens at the end of the download, drag the Orange Canvas
   icon and drop it over the *Applications* folder icon.

3. Start Orange Canvas then select menu **Options > Add-ons...** (see
   :ref:`figure 1 <macosx_installation_fig1>`).

.. _macosx_installation_fig1:

.. figure:: figures/options_addons_menu_macosx.png
    :align: center
    :alt: How to open the Add-ons management dialog

    Figure 1: Opening the Add-ons management dialog in Orange Canvas.

4. In the window which has opened (see :ref:`figure 2
   <macosx_installation_fig2>`), click on **Refresh list**, check the
   *Orange-Textable* box then the **Ok** button (twice).

.. _macosx_installation_fig2:

.. figure:: figures/addons_management_dialog_macosx.png
    :align: center
    :alt: Orange Textable marked for installation

    Figure 2: Orange Textable marked for installation.

If step 4 was carried out correctly, the Orange Textable tab appears in the
list on the left of the window of Orange Canvas after having exited and
restarted the program.

**Only if step 4 was not correctly carried out:**

5. Go to `PyPI <https://pypi.python.org/pypi/Orange-Textable>`_ to download
   the source distribution of Orange Textable (*.tar.gz* file).

6. Decompress the archive then open a Terminal and navigate to the
   decompressed archive (see below for more details on this step). Then enter
   the following instruction::

       python setup.py install

   NB: if this process fails, it is sometimes possible to resolve the problem
   by replacing the instruction with this one::

       /Applications/Orange.app/Contents/MacOS/python setup.py install

   *In case of difficulty in "opening a Terminal and navigating to the
   decompressed archive...":*

   a. Drag and drop on the desktop the *Orange-Textable-X* file (where *X* is
      the version number, e.g. "1.5") which can be found in the downloaded
      archive.

   b. In **Finder > Applications > Utilities**, double-click on *Terminal*.

   c. In the Terminal, correctly enter the instruction::

        cd Desktop/Orange-Textable-X

      (where *X* still is the version number).

   d. Then enter the instruction::

        python setup.py install

      (or if necessary, the alternative instruction shown here above).

