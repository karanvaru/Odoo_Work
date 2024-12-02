# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Applicant(models.Model):
    _inherit = "hr.applicant"
    
    applicant_education_ids = fields.One2many(
        'applicant.education',
        'education_id',
        string='Educations'
    )
    applicant_employeement_ids = fields.One2many(
        'applicant.employeement',
        'employeement_id',
        string='Employeements'
    )
    applicant_family_ids = fields.One2many(
        'applicant.family',
        'family_id',
        string='Familys'
    )
    applicant_medical_ids = fields.One2many(
        'applicant.medical',
        'medical_id',
        string='Medical Checkup'
    )
    
    @api.multi
    def create_employee_from_applicant(self):
        result = super(Applicant,self).create_employee_from_applicant()
        for applicant in self:
            for i in applicant.applicant_education_ids:
                    self.env['applicant.education'].create({
                                                            'degree_id': i.degree_id.id,
                                                            'institute_id':i.institute_id.id,
                                                            'passing_year':i.passing_year,
                                                            'grade':i.grade,
                                                            'major_subject':i.major_subject,
                                                            'employee_id':applicant.emp_id.id,
                                                        })
            for i in applicant.applicant_employeement_ids:
                    self.env['applicant.employeement'].create({
                                                            'organization_id': i.organization_id.id,
                                                            'start_date':i.start_date,
                                                            'end_date':i.end_date,
                                                            'role':i.role,
                                                            'supervisor':i.supervisor,
                                                            'employee_id':applicant.emp_id.id,
                                                        })
            for i in applicant.applicant_family_ids:
                    self.env['applicant.family'].create({
                                                            'relation_id': i.relation_id.id,
                                                            'name':i.name,
                                                            'age':i.age,
                                                            'employee_id':applicant.emp_id.id,
                                                        })
            for i in applicant.applicant_medical_ids:
                    self.env['applicant.medical'].create({
                                                            'checkup_type_id': i.checkup_type_id.id,
                                                            'checkup_result':i.checkup_result,
                                                            'employee_id':applicant.emp_id.id,
                                                        })
            
        return result

class ApplicantEducation(models.Model):
    _name = 'applicant.education'
    _description = 'Applicant Education'
    
    degree_id = fields.Many2one(
        'hr.recruitment.degree',
        string='Degree',
        required=True,
    )
    institute_id = fields.Many2one(
        'applicant.institute',
        string='Institute',
        required=True,
    )
    passing_year = fields.Char(
        string='Passing Year',
    )
    grade = fields.Char(
        string='Grade/Class',
    )
    major_subject = fields.Char(
        string='Major Subjects',
    )
    education_id = fields.Many2one(
        'hr.applicant',
        string='Education',
#         required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee'
    )
    
class ApplicantInstitute(models.Model):
    _name = 'applicant.institute'
    _description = 'Applicant Institute'
    
    name = fields.Char(
        string='Name',
        required=True,
    )
    
class ApplicantEmployeement(models.Model):
    _name = 'applicant.employeement'
    _description = 'Applicant Employeement'
    
    organization_id = fields.Many2one(
        'applicant.organization',
        string='Organization',
        required=True,
    )
    start_date = fields.Date(
        string='Start Date',
        required=False,
    )
    end_date = fields.Date(
        string='End Date',
        required=False,
    )
    role = fields.Char(
        string='Responsibilities',
        required=False,
    )
    supervisor = fields.Char(
        string='Supervisor',
        required=False,
    )
    employeement_id = fields.Many2one(
        'hr.applicant',
        string='Employeement'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee'
    )

class ApplicantOrganization(models.Model):
    _name = 'applicant.organization'
    _description = 'Applicant Organization'
    
    name = fields.Char(
        string='Name',
        required=True,
    )

class ApplicantFamily(models.Model):
    _name = 'applicant.family'
    _description = 'Applicant Family'
    
    relation_id = fields.Many2one(
        'applicant.relation',
        string='Relation',
        required=True,
    )
    name = fields.Char(
        string='Name',
        required=False,
    )
    age =fields.Integer(
        string='Age',
        required=False,
    )
    family_id = fields.Many2one(
        'hr.applicant',
        string='Family',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee'
    )

class ApplicantRelation(models.Model):
    _name = 'applicant.relation'
    _description = 'Applicant Relation'
    
    name = fields.Char(
        string='Name',
        required=True,
    )

class ApplicantMedical(models.Model):
    _name = 'applicant.medical'
    _description = 'Applicant Medical Details'
    
    checkup_type_id = fields.Many2one(
        'applicant.medical.checkup',
        string='Medical Test',
        required=True,
    )
    checkup_result = fields.Char(
        string='Result',
        required=False,
    )
    medical_id = fields.Many2one(
        'hr.applicant',
        string='Medical',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee'
    )

class ApplicantMedicalCheckup(models.Model):
    _name = 'applicant.medical.checkup'
    _description = 'Applicant Medical Checkup'
    
    name = fields.Char(
        string='Name',
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: