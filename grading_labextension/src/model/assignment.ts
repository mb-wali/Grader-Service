/**
 * Grader Extension API Schemas
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


export interface Assignment { 
    id?: number;
    name?: string;
    type?: Assignment.TypeEnum;
    due_date?: string;
    status?: Assignment.StatusEnum;
    points?: number;
}
export namespace Assignment {
    export type TypeEnum = 'user' | 'group';
    export const TypeEnum = {
        User: 'user' as TypeEnum,
        Group: 'group' as TypeEnum
    };
    export type StatusEnum = 'created' | 'pushed' | 'released' | 'fetching' | 'fetched' | 'complete';
    export const StatusEnum = {
        Created: 'created' as StatusEnum,
        Pushed: 'pushed' as StatusEnum,
        Released: 'released' as StatusEnum,
        Fetching: 'fetching' as StatusEnum,
        Fetched: 'fetched' as StatusEnum,
        Complete: 'complete' as StatusEnum
    };
}


