from ftfy import fix_text

with open("ProverbsADay\\proverbs.txt", encoding="utf-8", errors='replace') as f:
    content = f.read()

fix_content = fix_text(content)
fixed_content = fix_content.replace("�", "-")
with open("ProverbsADay\\proverbs_cleaned.txt", "w", encoding="utf-8") as f:
    f.write(fixed_content)


file = open("ProverbsADay\\proverbs_cleaned.txt", encoding="utf-8", errors='-')
writ = open("ProverbsADay/new_proverbs.txt", 'w')
prov = file.readlines()
#print(prov)
nums = ['1','2','3','4','5','6','7','8','9', '0']
foot = ['[a]','[b]','[c]']
prob = ''
chapter = 9
for i in prov:
    for j in foot:
        if j in i:
            i = i.replace(j,'')
    if i[0] in nums:
        if i[0] == '1' and not(i[1] in nums):
            chapter += 1
        prob += str(chapter)+':'+i.strip('\n')
    elif '    ' in i:
        prob += ' ' + i.strip()
    elif i == '\n':
        writ.write(prob+'\n')
        prob = ''
writ.write(prob+'\n')
file.close()
writ.close()


    