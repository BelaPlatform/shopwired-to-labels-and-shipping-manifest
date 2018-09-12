# Shopwired exports to labels and shipping manifest

This set of python and LaTeX scripts was created with the intention of generating readable and easier to interpret documents from Shopwired exports and shipping labels based on these.
In addition, it generates a .csv file that can be uploaded to Post Office [Drop and go (UK)](https://www.postoffice.co.uk/dropandgo) to generate shipping manifests.


NOTE: This scripts have been tailored for the different items on [our shop](https://shop.bela.io/) and therefore would need editing if these change.

## Instructions

1. Export orders .csv and copy it to the same folder the script lives on.

2. Run the shell script passing the export as the 1st parameter:		
  ```
  sh build_orders.sh <order_export.csv>
  ```
3. The script should generate several files:
  * `MANIFEST.csv` - csv file to use with Royal Mail's drop n go.
	* `NEW_ORDER.csv` - csv file used by the latex script to generate the labels
  * `items_to_ship.txt` - txt file indicating a summary of the items that are being shipped extracted from all orders
  * `order_info.txt`- txt file with a summary of the orders including order ID, address & comments.
  * `addres_label_14_a4.pdf` contains the pdf labels

4. Upload the `MANIFEST.csv` file to https://www.postoffice.co.uk/dropandgo to generate the manifest. 
If there is something odd on the pdf that this page renders, you can edit it manually after uploading the csv. You can also edit the csv before uploading, but I found the post office's page does some unpredictable stuff so it is better to edit it there.
