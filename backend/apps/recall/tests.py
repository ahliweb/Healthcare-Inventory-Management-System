from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.items.models import Category, FundingSource, Item, Location, Supplier, Unit
from apps.recall.models import Recall, RecallItem
from apps.stock.models import Stock, Transaction
from apps.users.models import User


class RecallVerifyWorkflowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='gudang_recall',
            password='secret123',
            role=User.Role.GUDANG,
        )

        self.unit = Unit.objects.create(code='TAB', name='Tablet')
        self.category = Category.objects.create(code='TABLET', name='Tablet', sort_order=1)
        self.item = Item.objects.create(
            nama_barang='Paracetamol 500mg',
            satuan=self.unit,
            kategori=self.category,
            minimum_stock=Decimal('0'),
        )
        self.location = Location.objects.create(code='LOC-01', name='Gudang Utama')
        self.funding_source = FundingSource.objects.create(code='DAK', name='Dana Alokasi Khusus')
        self.supplier = Supplier.objects.create(code='SUP-01', name='Supplier A')

        self.stock = Stock.objects.create(
            item=self.item,
            location=self.location,
            batch_lot='BATCH-001',
            expiry_date='2027-12-31',
            quantity=Decimal('100'),
            reserved=Decimal('0'),
            unit_price=Decimal('1000'),
            sumber_dana=self.funding_source,
        )

    def test_verify_recall_deducts_stock_and_creates_transaction(self):
        recall = Recall.objects.create(
            recall_date='2026-02-27',
            supplier=self.supplier,
            status=Recall.Status.SUBMITTED,
            created_by=self.user,
        )
        RecallItem.objects.create(
            recall=recall,
            item=self.item,
            stock=self.stock,
            quantity=Decimal('10'),
            notes='Kemasan rusak',
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('recall:recall_verify', args=[recall.pk]))

        self.assertEqual(response.status_code, 302)

        recall.refresh_from_db()
        self.stock.refresh_from_db()

        self.assertEqual(recall.status, Recall.Status.VERIFIED)
        self.assertEqual(recall.verified_by, self.user)
        self.assertEqual(self.stock.quantity, Decimal('90'))

        transaction = Transaction.objects.get(reference_type=Transaction.ReferenceType.RECALL, reference_id=recall.id)
        self.assertEqual(transaction.transaction_type, Transaction.TransactionType.OUT)
        self.assertEqual(transaction.quantity, Decimal('10'))

    def test_complete_recall_after_verified(self):
        recall = Recall.objects.create(
            recall_date='2026-02-27',
            supplier=self.supplier,
            status=Recall.Status.VERIFIED,
            created_by=self.user,
            verified_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('recall:recall_complete', args=[recall.pk]))

        self.assertEqual(response.status_code, 302)
        recall.refresh_from_db()
        self.assertEqual(recall.status, Recall.Status.COMPLETED)
