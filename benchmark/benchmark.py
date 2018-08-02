from textwrap import dedent
import os

specimen = "et4"
for np in [4, 8, 16, 32, 64]:
    for mdl in ["e", "ep"]:
        for sign, s in zip(["positive", "negative"], ["+", "-"]):
            for amount in [0.0, 0.5, 1.0, 3.0, 5.0]:
                if sign == "negative":
                    amount *= -1
                    if amount == 0.0:
                        continue

                if mdl == "ep":
                    model = dedent("""E = 17000.0
                        yield_stress = 175
                        Et = 850
                        """)
                    job_time = "72:00:00"
                else:
                    model = dedent("""\
                    E = 17000.0
                    """)
                    job_time = "72:00:00"

                job_name = specimen+mdl+str(amount)+"-"+str(np)

                opts = {"sign": sign, "amount": amount,
                        "model": model, "name": job_name, "time": job_time,
                        "np": np, "specimen":specimen}

                os.mkdir(job_name)
                os.chdir(job_name)

                with open("microFE.ini", 'w') as f:
                    f.write(dedent("""\
                        [directories]
                        CT_IMAGE_FOLDER = /fastdata/me1ame/microFE/images/{specimen}/
                        OUTPUT_DIR = /fastdata/me1ame/b4/{name}/
                        MESHER_SRC = /fastdata/me1ame/microFE/m_files/
                        LD_LIB_PATH = /usr/local/packages/apps/matlab/2016a/binary

                        [images]
                        img_name = Scan1_crop.dcm

                        [mesher]
                        threshold = 19000
                        resolution = 19.92

                        [fem]
                        boundary_condition = displacement
                        units = percent
                        sign = {sign}
                        amount = {amount}
                        direction = z
                        constrain = full
                        {model}

                        [job]
                        name = {name}
                        np = {np}""".format(**opts)))

                with open("mFE.sh", 'w') as f:
                    f.write(dedent("""\
                    #!/bin/bash
                    #$ -M a.melis@sheffield.ac.uk
                    #$ -m bea
                    #$ -P insigneo-imsb
                    #$ -q insigneo-imsb.q
                    #$ -l h_rt={time}
                    #$ -l rmem=500G
                    #$ -N {name}
                    #$ -pe mpi-rsh {np}
                    #$ -j y

                    module load apps/matlab/2016a/binary
                    module load apps/ansys/17.2

                    module load apps/python/conda
                    source activate tf

                    python /fastdata/me1ame/microFE/microFE.py -c microFE.ini""".format(**opts)))

                os.system("qsub mFE.sh")

                os.chdir("..")
