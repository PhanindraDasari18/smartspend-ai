export type TxType='income'|'expense'|'refund';
export type Transaction={id?:string;occurred_on:string;description:string;merchant?:string|null;amount:number;transaction_type:TxType;category:string;payment_method?:string|null;source?:'manual'|'import'|'demo';import_fingerprint?:string|null};
export type Budget={id?:string;month_start:string;category:string;limit_amount:number};
