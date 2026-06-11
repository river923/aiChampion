from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib import messages
from django.utils import timezone

from secretstore.crypto import encrypt_secret
from secretstore.models import SecretCredential
from secretstore.services import SecretConnectionError, test_credential_connection


class SecretCredentialForm(forms.ModelForm):
    api_key = forms.CharField(
        label="API 키",
        required=False,
        widget=forms.PasswordInput(render_value=False),
    )

    class Meta:
        model = SecretCredential
        fields = (
            "provider",
            "display_name",
            "api_key",
            "model_name",
            "is_active",
        )

    def save(self, commit: bool = True) -> SecretCredential:
        instance = super().save(commit=False)
        api_key = self.cleaned_data.get("api_key", "")
        if api_key:
            instance.encrypted_api_key = encrypt_secret(api_key)
            instance.key_last4 = api_key[-4:]
            instance.rotated_at = timezone.now()
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        api_key = cleaned_data.get("api_key", "")
        provider = cleaned_data.get("provider", "")
        if self.instance.pk is None and not api_key and provider != "local":
            raise forms.ValidationError("새 API 키 등록 시 API 키를 입력해야 합니다.")
        return cleaned_data


@admin.register(SecretCredential)
class SecretCredentialAdmin(ModelAdmin):
    form = SecretCredentialForm
    list_display = (
        "provider",
        "display_name",
        "masked_key",
        "model_name",
        "is_active",
        "last_tested_at",
        "updated_at",
    )
    list_filter = ("provider", "is_active")
    search_fields = ("display_name", "model_name")
    readonly_fields = ("key_last4", "last_tested_at", "rotated_at", "created_by")
    actions = ["test_selected_credentials"]

    class Media:
        js = ("secretstore/js/fetch_openrouter_models.js",)

    def save_model(
        self,
        request: object,
        obj: SecretCredential,
        form: forms.ModelForm,
        change: bool,
    ) -> None:
        if obj.created_by_id is None and hasattr(request, "user"):
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="선택한 API 키 연결 테스트")
    def test_selected_credentials(
        self,
        request: object,
        queryset: object,
    ) -> None:
        success_count = 0
        for credential in queryset:
            try:
                test_credential_connection(credential)
            except SecretConnectionError:
                self.message_user(
                    request,
                    f"{credential.display_name} 연결 테스트에 실패했습니다.",
                    messages.ERROR,
                )
                continue
            success_count += 1
        if success_count:
            self.message_user(
                request,
                f"{success_count}개 API 키 연결 테스트가 성공했습니다.",
                messages.SUCCESS,
            )

# Register your models here.
