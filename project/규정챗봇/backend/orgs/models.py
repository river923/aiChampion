from django.db import models
from treebeard.mp_tree import MP_Node


class OrganizationUnit(MP_Node):
    class UnitKind(models.TextChoices):
        INSTITUTION = "institution", "기관"
        HEADQUARTERS = "headquarters", "본부"
        OFFICE = "office", "실"
        TEAM = "team", "팀"

    name = models.CharField(max_length=120, verbose_name="조직/부서명")
    kind = models.CharField(max_length=24, choices=UnitKind.choices, verbose_name="조직 유형")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        verbose_name = "부서/조직"
        verbose_name_plural = "부서/조직 목록"

    node_order_by = ["name"]

    def __str__(self) -> str:
        return self.name


class StaffProfile(models.Model):
    organization = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.PROTECT,
        related_name="staff_members",
        verbose_name="소속 조직",
    )
    display_name = models.CharField(max_length=80, verbose_name="이름")
    position = models.CharField(max_length=80, blank=True, verbose_name="직급/직책")
    extension = models.CharField(max_length=40, blank=True, verbose_name="내선 번호")
    email = models.EmailField(blank=True, verbose_name="이메일")
    duty_keywords = models.TextField(blank=True, verbose_name="담당 업무")
    is_demo = models.BooleanField(default=True, verbose_name="데모 계정 여부")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        verbose_name = "임직원(데모)"
        verbose_name_plural = "임직원 목록"
        ordering = ["organization__name", "display_name"]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.organization})"

# Create your models here.
