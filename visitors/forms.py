from django import forms
from .models import Visitor
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from crispy_forms.bootstrap import FormActions

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['name', 'phone', 'address', 'visit_request', 'visit_status', 'visit_date', 'sms_opt_in']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'name': 'Full Name',
            'phone': 'Phone Number',
            'address': 'Address',
            'source': 'How Did You Hear About Us?',
            'visit_request': 'Request a Home Visit?',
            'visit_date': 'Preferred Visit Date',
            'visit_status': 'Visit Status',
            'sms_opt_in': 'Opt-In for SMS Updates',
        }
        help_texts = {
            'name': 'Please enter your full name (e.g., John Doe)',
            'phone': 'Enter a valid phone number (e.g., 123-456-7890)',
            'address': 'Include street, city, state, and ZIP code',
            'source': 'Where did you learn about Sarasota Gospel Temple?',
            'visit_date': 'Select your preferred date for a visit or service',
            'sms_opt_in': 'Receive text updates about services and events',
        }
        error_messages = {
            'name': {
                'required': 'Please provide your full name.',
                'max_length': 'Name must be less than 255 characters.',
            },
            'phone': {
                'required': 'A phone number is required.',
                'invalid': 'Please enter a valid phone number.',
            },
        }
        
    # forms.py
class ContactForm(forms.Form):
    name = forms.CharField(max_length=255, label="Your Name", required=True)
    email = forms.EmailField(label="Your Email", required=True)
    message = forms.CharField(widget=forms.Textarea, label="Message", required=True)
    
    # Custom field validation
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.replace('-', '').replace(' ', '').isdigit() or len(phone.replace('-', '').replace(' ', '')) < 10:
            raise forms.ValidationError("Please enter a valid 10-digit phone number (e.g., 123-456-7890)")
        return phone

    # Use SelectDateWidget for visit_date with year range
    visit_date = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2025, 2030)),
        help_text="Select your preferred visit date (between 2025 and 2029)"
    )

    # Custom widget for visit_request to use radio buttons for better UX
    visit_request = forms.ChoiceField(
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.RadioSelect,
        required=True,
        help_text="Would you like a home visit?"
    )

    # Custom widget for sms_opt_in to use a checkbox with a label
    sms_opt_in = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I agree to receive SMS updates about services and events"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'row g-3 needs-validation'
        self.helper.form_method = 'post'
        self.helper.form_action = 'visitor_form'
        self.helper.form_id = 'visitorForm'
        self.helper.label_class = 'form-label'
        self.helper.field_class = 'col-md-6'
        self.helper.field_template = 'bootstrap5/field.html'
        self.helper.layout = Layout(
            Field('name', wrapper_class='col-md-12'),
            Field('phone', wrapper_class='col-md-6'),
            Field('address', wrapper_class='col-md-12'),
            Field('source', wrapper_class='col-md-6'),
            Field('visit_request', wrapper_class='col-md-6', template='bootstrap5/radio.html'),
            Field('visit_date', wrapper_class='col-md-6'),
            Field('visit_status', wrapper_class='col-md-6'),
            Field('sms_opt_in', wrapper_class='col-md-6', template='bootstrap5/checkbox.html'),
            FormActions(
                Submit('submit', 'Submit', css_class='btn btn-success w-100 mt-3'),
            )
        )
        self.helper.attrs = {'novalidate': True}

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance