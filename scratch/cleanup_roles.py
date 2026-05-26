from django.contrib.auth.models import User
from accounts.models import BusinessProfile

admin_user = User.objects.filter(username='admin').first()
if admin_user and hasattr(admin_user, 'business'):
    biz = admin_user.business
    # Reassign this business to testuser_qa
    test_user, _ = User.objects.get_or_create(username='testuser_qa', defaults={'email': 'test@example.com'})
    if not test_user.check_password('user123'):
        test_user.set_password('user123')
        test_user.save()
    
    # Check if test_user already has a business
    if hasattr(test_user, 'business') and test_user.business != biz:
        test_user.business.delete()
    
    biz.user = test_user
    biz.save()
    print("Successfully unlinked 'admin' and assigned business to 'testuser_qa'")
else:
    print("Admin has no business attached.")
