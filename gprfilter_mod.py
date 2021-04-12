'''
->The code needs raw headers in following order: Filename, Dist, Lat, Long, Depth
->The code calculates first row of code by averaging data from 0 to interval/2, 
then from interval/2 to (interval + interval/2) and so on...
'''
import csv
import numpy as np
import math
filename = []
latitude = []
longitude = []
distance = []
depth = []
#reading csv file
#file_name=input("Enter filename.csv")
with open('41_61_LAYERS.csv') as csvfile:
    csvReader = csv.reader(csvfile)#importing raw data into blank python arrays
    for row in csvReader:
        filename.append(row[0])
        latitude.append(row[2])
        longitude.append(row[3])
        distance.append(row[1])
        depth.append(row[4])

#creating individual arrays with proper data types, converts blank depths to 0            
fname_arr=np.array(filename[1:],dtype=str)#importing data from python arrays to numpy arrays for favorable datatype
lat_arr=np.array(latitude[1:],dtype=float)#row starts from 1 not 0 to ignore heading row
long_arr=np.array(longitude[1:],dtype=float)
dist_arr=np.array(distance[1:],dtype=float)
rows_total=dist_arr.shape[0] #total number of GPR data pts
depth_arr=np.zeros((rows_total),dtype=float)#no need to mention no. of columns if it's a list
for i in range(1,rows_total):#converts blank values --> 0
    if not depth[i]:
        depth_arr[i-1]=0
    else:
        depth_arr[i-1]=depth[i]

combine_arr=np.array((fname_arr,lat_arr,long_arr,dist_arr,depth_arr)).T # 1 multi dim array with all rows
#deleting rows with 0 depth in the modified 'mod_arr'
blanks=np.zeros((1),dtype=float)
for j in range(0,rows_total):#noting blank row numbers
    if (depth_arr[j]==0):
        blanks=np.append(blanks,j)
    else:
        pass
blanks=blanks[1:]#removing first 0-element row created while declaring blank array
#creating MOD array with non-zero depths
mod_arr=np.delete(np.array((lat_arr,long_arr,dist_arr,depth_arr)).T,blanks,0)
#calculating absolute distance
mod_arr=np.hstack((mod_arr,np.zeros((mod_arr.shape[0],1))))#adding blank row at end  
for k in range(1,mod_arr.shape[0]):
    if (mod_arr[k,2]>mod_arr[k-1,2]):
        mod_arr[k,4]=mod_arr[k-1,4]+mod_arr[k,2]-mod_arr[k-1,2]
    else:
        mod_arr[k,4]=mod_arr[k-1,4]+mod_arr[k,2]
#rounding absolute distnace to nearest integer
mod_arr=np.hstack((mod_arr,np.zeros((mod_arr.shape[0],1))))#adding blank row at end  
for k in range(1,mod_arr.shape[0]):
    mod_arr[k,5]=int(np.rint(mod_arr[k,4]))
#calculating average depths/lat-longs given interval distance
int_dist=int(input("Enter interval distance (in ft, integer):")) #ask user for interval distance
print("Outputting data every %s ft" % (int_dist))
'''
*Calculating output array
*We are avergaging lat/long every 25 feet as it approximates to calculating centroid
for distances withing 250 miles
'''
final_rows=int(np.rint(mod_arr[mod_arr.shape[0]-1,5]/int_dist))
final_arr=np.zeros((20000,4),dtype=float)
#first, 0th row, we average from 0 to interval/2 ft.
first_row=np.max(np.where(mod_arr[:,5]==(int_dist/2)))
final_arr[0,0]=np.mean(mod_arr[0:first_row,0])#avg lat of the interval
final_arr[0,1]=np.mean(mod_arr[0:first_row,1])#avg long of the interval
final_arr[0,2]=np.mean(mod_arr[0:first_row,3])#avg depth of the interval
final_arr[0,3]=int_dist/2 #distance
start_row=first_row+1
end_row=0
for k in range(1,final_rows+1):
    try:#try-except part of code written to overcome the error
        end_row=int(np.max(np.where(mod_arr[:,5]==k*int_dist)))#finding last row in desired dist interval
    except ValueError:
        pass
    if math.isnan(np.mean(mod_arr[start_row:end_row,0])):#to check Nan (blank) values
        pass
    else:
        final_arr[k,0]=np.mean(mod_arr[start_row:end_row,0])#avg lat of the interval
        final_arr[k,1]=np.mean(mod_arr[start_row:end_row,1])#avg long of the interval
        final_arr[k,2]=np.mean(mod_arr[start_row:end_row,3])#avg depth of the interval
        final_arr[k,3]=k*int_dist
        start_row=end_row+1
#to average (n-1)th interval to the end of the data
final_arr[final_rows,0]=np.mean(mod_arr[start_row:,0])#avg lat
final_arr[final_rows,1]=np.mean(mod_arr[start_row:,1])#avg long
final_arr[final_rows,2]=np.mean(mod_arr[start_row:,3])#avg depth
final_arr[final_rows,3]=int(np.mean(mod_arr[start_row:,5]))#distance
final_arr = final_arr[~np.all(final_arr == 0, axis=1)]#removing blank rows
np.savetxt("modarr.csv",mod_arr,delimiter=",")
np.savetxt("output.csv",final_arr,delimiter=",")
