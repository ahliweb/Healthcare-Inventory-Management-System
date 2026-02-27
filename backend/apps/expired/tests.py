from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.expired.models import Expired, ExpiredItem
from apps.items.models import Category, FundingSource, Item, Location, Unit
from apps.stock.models import Stock, Transaction
from apps.users.models import User


class ExpiredVerifyWorkflowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='gudang_expired',
            password='secret123',
            role=User.Role.GUDANG,
        )

        self.unit = Unit.objects.create(code='BOT', name='Botol')
        self.category = Category.objects.create(code='SYRUP', name='Sirup', sort_order=1)
        self.item = Item.objects.create(
            nama_barang='Sirup Cough 60ml',
            satuan=self.unit,
            kategori=self.category,
            minimum_stock=Decimal('0'),
        )
        self.location = Location.objects.create(code='LOC-02', name='Gudang Farmasi')
        self.funding_source = FundingSource.objects.create(code='APBD', name='Anggaran APBD')

        self.stock = Stock.objects.create(
            item=self.item,
            location=self.location,
            batch_lot='BATCH-EXP-01',
            expiry_date='2026-01-01',
            quantity=Decimal('50'),
            reserved=Decimal('0'),
            unit_price=Decimal('2500'),
            sumber_dana=self.funding_source,
        )

    def test_verify_expired_deducts_stock_and_creates_transaction(self):
        expired_doc = Expired.objects.create(
            report_date='2026-02-27',
            status=Expired.Status.SUBMITTED,
            created_by=self.user,
        )
        ExpiredItem.objects.create(
            expired=expired_doc,
            item=self.item,
            stock=self.stock,
            quantity=Decimal('5'),
            notes='Melewati tanggal ED',
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('expired:expired_verify', args=[expired_doc.pk]))

        self.assertEqual(response.status_code, 302)

        expired_doc.refresh_from_db()
        self.stock.refresh_from_db()

        self.assertEqual(expired_doc.status, Expired.Status.VERIFIED)
        self.assertEqual(expired_doc.verified_by, self.user)
        self.assertEqual(self.stock.quantity, Decimal('45'))

        transaction = Transaction.objects.get(reference_type=Transaction.ReferenceType.EXPIRED, reference_id=expired_doc.id)
        self.assertEqual(transaction.transaction_type, Transaction.TransactionType.OUT)
        self.assertEqual(transaction.quantity, Decimal('5'))

    def test_dispose_expired_after_verified(self):
        expired_doc = Expired.objects.create(
            report_date='2026-02-27',
            status=Expired.Status.VERIFIED,
            created_by=self.user,
            verified_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('expired:expired_dispose', args=[expired_doc.pk]))

        self.assertEqual(response.status_code, 302)
        expired_doc.refresh_from_db()
        self.assertEqual(expired_doc.status, Expired.Status.DISPOSED)
