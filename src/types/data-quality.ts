export type ValidationCategoryType = 
  | 'SCHEMA' 
  | 'NULL_CHECK' 
  | 'DUPLICATE' 
  | 'CUSTOMER_FK' 
  | 'SKU_FK' 
  | 'DATA_TYPE';

export type IssueSeverity = 'CRITICAL' | 'WARNING' | 'INFO';

export interface ValidationCategorySummary {
  category: ValidationCategoryType;
  name: string;
  description: string;
  totalEvaluated: number;
  passedCount: number;
  failedCount: number;
  passRatePercentage: number;
  status: 'PASSED' | 'WARNING' | 'FAILED';
}

export interface DataQualityIssue {
  issueId: string;
  timestamp: string;
  category: ValidationCategoryType;
  ruleViolated: string;
  targetTable: string;
  targetColumn: string;
  recordIdentifier: string;
  severity: IssueSeverity;
  invalidValue: string;
  recommendation: string;
}

export interface DataQualitySummary {
  pipelineStatus: 'HEALTHY' | 'WARNING' | 'DEGRADED' | 'FAILED';
  lastRunTimestamp: string;
  totalRecordsProcessed: number;
  totalValidRecords: number;
  totalInvalidRecords: number;
  overallPassRate: number;
  categories: ValidationCategorySummary[];
  issuesCountBySeverity: {
    critical: number;
    warning: number;
    info: number;
  };
}

export interface DataQualityQueryParams {
  page?: number;
  pageSize?: number;
  category?: ValidationCategoryType | 'ALL';
  severity?: IssueSeverity | 'ALL';
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
