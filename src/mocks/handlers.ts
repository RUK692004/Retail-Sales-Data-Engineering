import { http, HttpResponse } from 'msw';
import {
  MOCK_DASHBOARD_SUMMARY,
  MOCK_SALES,
  MOCK_INVENTORY,
  MOCK_PRODUCTS,
  MOCK_CUSTOMERS,
  MOCK_PROMOTIONS,
  MOCK_DATA_QUALITY_SUMMARY,
  MOCK_DATA_QUALITY_ISSUES,
} from './mock-data';

export const handlers = [
  // Dashboard Summary
  http.get('/api/dashboard/summary', () => {
    return HttpResponse.json({
      data: MOCK_DASHBOARD_SUMMARY,
      timestamp: new Date().toISOString(),
    });
  }),

  // Sales List & Filtering
  http.get('/api/sales', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10', 10);
    const search = url.searchParams.get('search')?.toLowerCase() || '';
    const storeId = url.searchParams.get('storeId') || '';
    const category = url.searchParams.get('category') || '';
    const sortBy = url.searchParams.get('sortBy') || 'saleDate';
    const sortOrder = url.searchParams.get('sortOrder') || 'desc';

    let filtered = [...MOCK_SALES];

    if (search) {
      filtered = filtered.filter(
        (s) =>
          s.saleId.toLowerCase().includes(search) ||
          s.customerName.toLowerCase().includes(search) ||
          s.productName.toLowerCase().includes(search) ||
          s.storeName.toLowerCase().includes(search) ||
          s.skuId.toLowerCase().includes(search)
      );
    }

    if (storeId && storeId !== 'ALL') {
      filtered = filtered.filter((s) => s.storeId === storeId);
    }

    if (category && category !== 'ALL') {
      filtered = filtered.filter((s) => s.category.toLowerCase() === category.toLowerCase());
    }

    filtered.sort((a, b) => {
      let valA = (a as unknown as Record<string, unknown>)[sortBy];
      let valB = (b as unknown as Record<string, unknown>)[sortBy];
      if (valA === undefined) valA = '';
      if (valB === undefined) valB = '';

      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortOrder === 'asc' ? valA - valB : valB - valA;
      }
      return sortOrder === 'asc'
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    });

    const total = filtered.length;
    const totalPages = Math.ceil(total / pageSize) || 1;
    const startIndex = (page - 1) * pageSize;
    const paginatedData = filtered.slice(startIndex, startIndex + pageSize);

    return HttpResponse.json({
      data: paginatedData,
      meta: {
        total,
        page,
        pageSize,
        totalPages,
      },
    });
  }),

  // Sales Metrics Aggregate
  http.get('/api/sales/metrics', () => {
    const totalRevenue = MOCK_SALES.reduce((acc, curr) => acc + curr.totalAmount, 0);
    const totalQuantity = MOCK_SALES.reduce((acc, curr) => acc + curr.quantity, 0);
    const averageOrderValue = MOCK_SALES.length ? totalRevenue / MOCK_SALES.length : 0;

    return HttpResponse.json({
      data: {
        totalSalesCount: MOCK_SALES.length,
        totalRevenue,
        averageOrderValue,
        totalQuantitySold: totalQuantity,
      },
    });
  }),

  // Inventory List & Monitoring
  http.get('/api/inventory', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10', 10);
    const search = url.searchParams.get('search')?.toLowerCase() || '';
    const storeId = url.searchParams.get('storeId') || '';
    const status = url.searchParams.get('status') || '';
    const sortBy = url.searchParams.get('sortBy') || 'stockOnHand';
    const sortOrder = url.searchParams.get('sortOrder') || 'asc';

    let filtered = [...MOCK_INVENTORY];

    if (search) {
      filtered = filtered.filter(
        (inv) =>
          inv.productName.toLowerCase().includes(search) ||
          inv.skuId.toLowerCase().includes(search) ||
          inv.storeName.toLowerCase().includes(search) ||
          inv.category.toLowerCase().includes(search)
      );
    }

    if (storeId && storeId !== 'ALL') {
      filtered = filtered.filter((inv) => inv.storeId === storeId);
    }

    if (status && status !== 'ALL') {
      filtered = filtered.filter((inv) => inv.status === status);
    }

    filtered.sort((a, b) => {
      let valA = (a as unknown as Record<string, unknown>)[sortBy];
      let valB = (b as unknown as Record<string, unknown>)[sortBy];
      if (valA === undefined) valA = '';
      if (valB === undefined) valB = '';

      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortOrder === 'asc' ? valA - valB : valB - valA;
      }
      return sortOrder === 'asc'
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    });

    const total = filtered.length;
    const totalPages = Math.ceil(total / pageSize) || 1;
    const startIndex = (page - 1) * pageSize;
    const paginatedData = filtered.slice(startIndex, startIndex + pageSize);

    return HttpResponse.json({
      data: paginatedData,
      meta: {
        total,
        page,
        pageSize,
        totalPages,
      },
    });
  }),

  // Products / SKUs List
  http.get('/api/products', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10', 10);
    const search = url.searchParams.get('search')?.toLowerCase() || '';
    const category = url.searchParams.get('category') || '';
    const status = url.searchParams.get('status') || '';
    const sortBy = url.searchParams.get('sortBy') || 'skuId';
    const sortOrder = url.searchParams.get('sortOrder') || 'asc';

    let filtered = [...MOCK_PRODUCTS];

    if (search) {
      filtered = filtered.filter(
        (p) =>
          p.skuId.toLowerCase().includes(search) ||
          p.productName.toLowerCase().includes(search) ||
          p.brand.toLowerCase().includes(search) ||
          p.category.toLowerCase().includes(search)
      );
    }

    if (category && category !== 'ALL') {
      filtered = filtered.filter((p) => p.category.toLowerCase() === category.toLowerCase());
    }

    if (status && status !== 'ALL') {
      filtered = filtered.filter((p) => p.status === status);
    }

    filtered.sort((a, b) => {
      let valA = (a as unknown as Record<string, unknown>)[sortBy];
      let valB = (b as unknown as Record<string, unknown>)[sortBy];
      if (valA === undefined) valA = '';
      if (valB === undefined) valB = '';

      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortOrder === 'asc' ? valA - valB : valB - valA;
      }
      return sortOrder === 'asc'
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    });

    const total = filtered.length;
    const totalPages = Math.ceil(total / pageSize) || 1;
    const startIndex = (page - 1) * pageSize;
    const paginatedData = filtered.slice(startIndex, startIndex + pageSize);

    return HttpResponse.json({
      data: paginatedData,
      meta: {
        total,
        page,
        pageSize,
        totalPages,
      },
    });
  }),

  // Single Product Detail
  http.get('/api/products/:skuId', ({ params }) => {
    const { skuId } = params;
    const product = MOCK_PRODUCTS.find((p) => p.skuId === skuId);
    if (!product) {
      return new HttpResponse(JSON.stringify({ message: 'Product SKU not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return HttpResponse.json({ data: product });
  }),

  // Customers List
  http.get('/api/customers', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10', 10);
    const search = url.searchParams.get('search')?.toLowerCase() || '';
    const loyaltyTier = url.searchParams.get('loyaltyTier') || '';
    const sortBy = url.searchParams.get('sortBy') || 'totalPurchases';
    const sortOrder = url.searchParams.get('sortOrder') || 'desc';

    let filtered = [...MOCK_CUSTOMERS];

    if (search) {
      filtered = filtered.filter(
        (c) =>
          c.customerId.toLowerCase().includes(search) ||
          c.fullName.toLowerCase().includes(search) ||
          c.email.toLowerCase().includes(search) ||
          c.city.toLowerCase().includes(search)
      );
    }

    if (loyaltyTier && loyaltyTier !== 'ALL') {
      filtered = filtered.filter((c) => c.loyaltyTier === loyaltyTier);
    }

    filtered.sort((a, b) => {
      let valA = (a as unknown as Record<string, unknown>)[sortBy];
      let valB = (b as unknown as Record<string, unknown>)[sortBy];
      if (valA === undefined) valA = '';
      if (valB === undefined) valB = '';

      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortOrder === 'asc' ? valA - valB : valB - valA;
      }
      return sortOrder === 'asc'
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    });

    const total = filtered.length;
    const totalPages = Math.ceil(total / pageSize) || 1;
    const startIndex = (page - 1) * pageSize;
    const paginatedData = filtered.slice(startIndex, startIndex + pageSize);

    return HttpResponse.json({
      data: paginatedData,
      meta: {
        total,
        page,
        pageSize,
        totalPages,
      },
    });
  }),

  // Single Customer Detail
  http.get('/api/customers/:customerId', ({ params }) => {
    const { customerId } = params;
    const customer = MOCK_CUSTOMERS.find((c) => c.customerId === customerId);
    if (!customer) {
      return new HttpResponse(JSON.stringify({ message: 'Customer not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return HttpResponse.json({ data: customer });
  }),

  // Promotions List
  http.get('/api/promotions', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10', 10);
    const search = url.searchParams.get('search')?.toLowerCase() || '';
    const status = url.searchParams.get('status') || '';
    const sortBy = url.searchParams.get('sortBy') || 'startDate';
    const sortOrder = url.searchParams.get('sortOrder') || 'desc';

    let filtered = [...MOCK_PROMOTIONS];

    if (search) {
      filtered = filtered.filter(
        (p) =>
          p.promotionId.toLowerCase().includes(search) ||
          p.promotionName.toLowerCase().includes(search) ||
          p.targetValue.toLowerCase().includes(search)
      );
    }

    if (status && status !== 'ALL') {
      filtered = filtered.filter((p) => p.status === status);
    }

    filtered.sort((a, b) => {
      let valA = (a as unknown as Record<string, unknown>)[sortBy];
      let valB = (b as unknown as Record<string, unknown>)[sortBy];
      if (valA === undefined) valA = '';
      if (valB === undefined) valB = '';

      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortOrder === 'asc' ? valA - valB : valB - valA;
      }
      return sortOrder === 'asc'
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    });

    const total = filtered.length;
    const totalPages = Math.ceil(total / pageSize) || 1;
    const startIndex = (page - 1) * pageSize;
    const paginatedData = filtered.slice(startIndex, startIndex + pageSize);

    return HttpResponse.json({
      data: paginatedData,
      meta: {
        total,
        page,
        pageSize,
        totalPages,
      },
    });
  }),

  // Data Quality Summary
  http.get('/api/data-quality/summary', () => {
    return HttpResponse.json({
      data: MOCK_DATA_QUALITY_SUMMARY,
      timestamp: new Date().toISOString(),
    });
  }),

  // Data Quality Issues List
  http.get('/api/data-quality/issues', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10', 10);
    const search = url.searchParams.get('search')?.toLowerCase() || '';
    const category = url.searchParams.get('category') || '';
    const severity = url.searchParams.get('severity') || '';

    let filtered = [...MOCK_DATA_QUALITY_ISSUES];

    if (search) {
      filtered = filtered.filter(
        (i) =>
          i.issueId.toLowerCase().includes(search) ||
          i.ruleViolated.toLowerCase().includes(search) ||
          i.targetTable.toLowerCase().includes(search) ||
          i.recordIdentifier.toLowerCase().includes(search)
      );
    }

    if (category && category !== 'ALL') {
      filtered = filtered.filter((i) => i.category === category);
    }

    if (severity && severity !== 'ALL') {
      filtered = filtered.filter((i) => i.severity === severity);
    }

    const total = filtered.length;
    const totalPages = Math.ceil(total / pageSize) || 1;
    const startIndex = (page - 1) * pageSize;
    const paginatedData = filtered.slice(startIndex, startIndex + pageSize);

    return HttpResponse.json({
      data: paginatedData,
      meta: {
        total,
        page,
        pageSize,
        totalPages,
      },
    });
  }),
];
