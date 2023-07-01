listA = [1,2,3,4,5]

listB = [(i,i,i) for i in listA]

print (listA)
print (listB)

listC = ['Banana','Apple','Orange']

listD = ["prefix_{}".format(each) for each in listC]

print (listC)
print (listD)

dictA ={'name':'Max','Age':20}
dictB = {'name':'Tim','Email':"@gmail"}

dictA.update(dictB)
print(dictA)

new_string = 'A+B '.join(listC)
print(new_string)

for fruit in listC:
    print (f"This fruit is {fruit}")
# mylist = []
# # Add item
# mylist.append("object")
# mylist.insert(id,"object")