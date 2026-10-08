# سَرْد (sard)

مهارة لـClaude تشرح أي نص أو فصل أو فكرة شرحًا سرديًا متسلسلًا: تبدأ من الأساس، ثم تتنقل بين المحطات بروابط منطقية صادقة (أولًا، ولهذا، ثم يتضح، ومن خلال ذلك...)، حتى تصل إلى المعنى النهائي. تشرح بلغة المستخدم، وتراعي مجال الموضوع ومصطلحاته وسياقه.

## التثبيت كإضافة (للخطط المدفوعة: Pro / Max / Team / Enterprise)
1. في Claude افتح **Customize** ثم **Plugins**.
2. اضغط **Add** ثم **Add marketplace** ثم **Add from a repository**.
3. اكتب اسم هذا المستودع بصيغة `owner/repo`.
4. ثبّت إضافة **sard** من القائمة.

**Claude Code:**
```
/plugin marketplace add owner/repo
/plugin install sard@sard
```

## التثبيت كمهارة مفردة (كل الخطط، ومنها المجانية)
1. نزّل الملف `sard.zip` من هذا المستودع.
2. فعّل **Code execution and file creation** من Settings ثم Capabilities.
3. افتح **Customize** ثم **Skills**، واضغط **+** ثم **Create skill** ثم **Upload a skill**، واختر الملف.

## الاستعمال
اطلب شرح أي فكرة أو فصل، أو اكتب `/sard`.
