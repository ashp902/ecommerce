from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User, Address

# ENUM type iterabel with gender field options
GENDER_MALE = "M"
GENDER_FEMALE = "F"
GENDER_OTHER = "O"
GENDER_CHOICES = [
    (GENDER_MALE, "Male"),
    (GENDER_FEMALE, "Female"),
    (GENDER_OTHER, "Other"),
]


# Form to create a new user
class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=255,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=255,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Last name"}),
    )
    date_of_birth = forms.DateField(
        widget=forms.widgets.DateInput(
            attrs={
                "placeholder": "Date of birth",
                "onfocus": '(this.type="date")',
                "onblur": '(this.type="text")',
            }
        )
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = "Email address"
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm password"

    # Save an user with seller role
    def save_seller(self):
        data = self.cleaned_data
        user = User(
            email=data["email"],
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=data["date_of_birth"],
            gender=data["gender"],
            user_role_id=2,
        )
        user.set_password(data["password1"])
        user.save()

    # Save an user with buyer role
    def save_buyer(self):
        data = self.cleaned_data
        user = User(
            email=data["email"],
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=data["date_of_birth"],
            gender=data["gender"],
            user_role_id=1,
        )
        user.set_password(data["password1"])
        user.save()

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
        ]


# Form for user login
class LoginUserForm(forms.Form):
    email = forms.EmailField(label="Email ID")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = "Email address"
        self.fields["password"].widget.attrs["placeholder"] = "Password"

    fields = ["email", "password"]


# Form to edit an user details
class EditUserForm(forms.Form):
    password1 = forms.CharField(
        label="New Password", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="Confirm New Password", widget=forms.PasswordInput, required=False
    )
    first_name = forms.CharField(max_length=255, label="First Name")
    last_name = forms.CharField(max_length=255, label="Last Name")
    date_of_birth = forms.DateField(
        widget=forms.widgets.DateInput(
            attrs={
                "placeholder": "Date of birth",
                "onfocus": '(this.type="date")',
                "onblur": '(this.type="text")',
            }
        )
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["placeholder"] = "New password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm new password"


# Form to create or edit an address
class AddressForm(forms.Form):
    address_name = forms.CharField(max_length=255, label="Address name")
    door_no = forms.CharField(max_length=255, label="Door Number")
    street = forms.CharField(max_length=255, label="Street")
    area = forms.CharField(max_length=255, label="Area")
    city = forms.CharField(max_length=255, label="City")
    state = forms.CharField(max_length=255, label="State")
    country = forms.CharField(max_length=255, label="Country")
    pincode = forms.IntegerField(label="Pincode")

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields["address_name"].widget.attrs["placeholder"] = "Address name"
        self.fields["door_no"].widget.attrs["placeholder"] = "Door number"
        self.fields["street"].widget.attrs["placeholder"] = "Street"
        self.fields["area"].widget.attrs["placeholder"] = "Area"
        self.fields["city"].widget.attrs["placeholder"] = "City"
        self.fields["state"].widget.attrs["placeholder"] = "State"
        self.fields["country"].widget.attrs["placeholder"] = "Country"
        self.fields["pincode"].widget.attrs["placeholder"] = "Pincode"

    # Save address with the current user id
    def save_with_user_id(self, user_id):
        data = self.cleaned_data
        address = Address(
            address_name=data["address_name"],
            door_no=data["door_no"],
            street=data["street"],
            area=data["area"],
            city=data["city"],
            state=data["state"],
            country=data["country"],
            pincode=data["pincode"],
            user_id=user_id,
        )

        address.save()

    class Meta:
        model = Address
        fields = [
            "address_name",
            "door_no",
            "street",
            "area",
            "city",
            "state",
            "country",
            "pincode",
        ]
